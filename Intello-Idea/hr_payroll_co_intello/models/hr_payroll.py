from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date

PERIODICITY = [('7', 'Weekly'), ('15', 'Biweekly'), ('30', 'Monthly')]


def get_years():
    years_choices = []
    for year in range(2020, 2101):
        years_choices.append(
            (str(year), str(year)))
    return years_choices


class HrPayrollType(models.Model):
    _name = 'hr.payroll.type'
    _description = 'Hr Payroll Type'

    name = fields.Char('Payroll Type')
    manage_periods = fields.Boolean('Manages Periods?')
    periodicity = fields.Selection(PERIODICITY, string='Periodicity')
    year = fields.Selection(get_years(), string='Year')
    start_period = fields.Date('Start Period')
    line_ids = fields.One2many('hr.period.lines', 'payroll_type_id')

    @api.onchange('year', 'start_period')
    def _verify_year_on_start_period(self):
        if self.year and self.start_period:
            if self.year != str(self.start_period.year):
                raise ValidationError(_('The year and the year of the beginning of the period must be the same.'))

    """Buttons"""

    def generate_period(self):
        self.line_ids.unlink()

        if self.periodicity:
            periodicity = int(self.periodicity)

            if self.year and self.start_period:
                period = 0
                year = int(self.year)

                while year == int(self.year):
                    date_from = self.start_period if period < 1 else date_from

                    if self.periodicity == '7':
                        date_to = date_from + relativedelta(days=periodicity - 1)

                    if self.periodicity == '15':

                        if date_from.day <= 15:
                            date_from = date_from.replace(day=1)
                            date_to = date_from.replace(day=15)

                        if date_from.day > 15:
                            date_from = date_from.replace(day=16)
                            date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                    if self.periodicity == '30':
                        date_from = date_from.replace(day=1)
                        date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                    period += 1
                    vals = {
                        'period': period,
                        'date_from': date_from,
                        'date_to': date_to,
                        'name': str(self.name) + " - " + format_date(self.env, date_to,
                                                                     date_format="MMMM") if not self.periodicity == '7' else str(
                            self.name) + " - " + str(
                            date_to.isocalendar()[1]) + " - " + str(self.year),
                        'payroll_type_id': self.id,
                    }

                    if self.periodicity in ['15', '30']:
                        date_from = date_from + relativedelta(months=1)

                    else:
                        date_from = date_from + relativedelta(days=periodicity)

                    year = int(date_from.year)
                    self.line_ids.create(vals)

    def confirm(self):
        for line in self.line_ids:
            line.state = 'confirmed'


class HrPeriodLines(models.Model):
    _name = 'hr.period.lines'
    _description = 'Hr Period Lines'

    name = fields.Char('Payment Type')
    period = fields.Char('Period')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft')

    payroll_type_id = fields.Many2one('hr.payroll.type')
