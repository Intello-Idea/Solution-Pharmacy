from odoo import api, fields, models, _, exceptions
from datetime import date

APPLICABLE_TO = [('first_fortnight', 'First fortnight'), ('second_fortnight', 'Second fortnight'),
                 ('both_weeks', 'Both weeks'), ('monthly', 'Monthly')]

STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'), ('canceled', 'Canceled')]


class HrConceptFixed(models.Model):
    _name = 'hr.concept.fixed'
    _inherit = 'mail.thread'
    _description = 'Concept Fixed For Payslip'

    def _default_name(self):
        name = _('New')
        return name

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  default=lambda self: self.env.company.currency_id.id)
    state = fields.Selection(selection=STATE, string='State', default='draft')

    name = fields.Char('Reference', default=_default_name)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    applicable_in = fields.Many2many('hr.payroll.type', string='Applicable In')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    input_type_id = fields.Many2one('hr.payslip.input.type', 'Input Type')
    value = fields.Monetary('Value')
    creation_date = fields.Date('Creation Date', default=date.today())
    validation_date = fields.Date('Validation Date')
    rrhh_manager_id = fields.Many2one('hr.employee', 'RRHH Manager')
    description = fields.Text('Description')
    input_line_ids = fields.One2many('hr.payslip.input', 'concept_id', 'Details')

    """Onchange Methods"""

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                self.contract_id = contract.id
            else:
                raise exceptions.ValidationError(_('The employee does not have an active contract'))

    """Buttons Methods"""

    def confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'confirmed'

    def validate(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'validated'
                rec.validation_date = date.today()

    def cancel(self):
        for rec in self:
            if rec.state == 'confirmed' or 'validated':
                rec.state = 'canceled'

    def draft(self):
        for rec in self:
            rec.state = 'draft'

    """Inherit Methods"""

    @api.model
    def create(self, vals):

        concept = super(HrConceptFixed, self).create(vals)

        if concept.name == _('New'):
            number = self.env['ir.sequence'].next_by_code('hr.concept.fixed', sequence_date=concept.creation_date)
            concept.write({
                'name': number
            })

        if concept.value <= 0:
            raise exceptions.ValidationError(_('Value must be greater than zero'))

        return concept
