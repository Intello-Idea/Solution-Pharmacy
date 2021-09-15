from odoo import api, fields, models, _, exceptions
from datetime import date

STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
         ('canceled', 'Canceled'), ('paid', 'Paid')]


class HrNovelty(models.Model):
    _name = 'hr.novelty'
    _description = 'Hr Novelty'
    _inherit = ['mail.thread']

    def _default_name(self):
        name = _('New')
        return name

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    name = fields.Char('Reference', default=_default_name, copy=False)
    state = fields.Selection(selection=STATE, default='draft', copy=False)

    employee_id = fields.Many2one('hr.employee', 'Employee')
    contract_id = fields.Many2one('hr.contract', 'Contract', )
    applicable_in = fields.Many2one('hr.payroll.type', 'Applicable In')
    novelty_date = fields.Date('Novelty Date')
    input_type_id = fields.Many2one('hr.payslip.input.type', 'Input Type')
    value = fields.Monetary('Value', copy=False)
    creation_date = fields.Date('Creation Date', default=date.today(), copy=False)
    validation_date = fields.Date('Validation Date', copy=False)
    rrhh_manager_id = fields.Many2one('hr.employee', 'RRHH Manager')
    description = fields.Text('Description', copy=False)

    input_line_ids = fields.One2many('hr.payslip.input', 'novelty_id', 'Details')
    payslip_id = fields.Many2one('hr.payslip', related='input_line_ids.payslip_id')
    payslip_id = fields.Many2one('hr.payslip', related='input_line_ids.payslip_id')

    @api.onchange('employee_id')
    def _charge_contract(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                self.contract_id = contract.id

    """Inherit Methods"""

    @api.model
    def create(self, vals):
        value = vals.get('value', False)
        if value <= 0:
            raise exceptions.ValidationError(_('Value cannot be less than 0'))

        novelty = super(HrNovelty, self).create(vals)

        if novelty.name == _('New'):
            number = self.env['ir.sequence'].next_by_code('hr.novelty',
                                                          sequence_date=novelty.creation_date)
        novelty.write({
            'name': number
        })

        return novelty

    """Buttons Methods"""

    def validate(self):
        for rec in self:
            rec.state = 'validated'
            rec.validation_date = date.today()

    def confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def cancel(self):
        for rec in self:
            rec.state = 'canceled'

    def go_to_draft(self):
        for rec in self:
            rec.state = 'draft'
