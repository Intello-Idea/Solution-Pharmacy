from odoo import api, fields, models, _
from datetime import date
from lxml import etree

REASON_TYPE = [('salary_change', 'Salary change'), ('change_administrator', 'Change administrator')]
TYPE_CHANGE = [('1', 'Temporary'), ('2', 'Permanent')]
TYPE_CHANGE_ADMINISTRATOR = [('is_eps', 'Health Care Provider (HCP)'), ('is_arl', 'Occupational Risk Manager (ORM)'),
                             ('is_ccf', 'Family Compensation Fund (FCF)'), ('pension_found', 'Pension Found'),
                             ('cesantia_fund', 'Cesantia Fund')]
STATE_TYPE_CHANGE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
                     ('canceled', 'Canceled')]


class HrMotivosCambios(models.Model):
    _name = 'hr.motivos.ccambios'
    _description = 'Change control for wage change reasons'

    name = fields.Char('Description', required=1)
    reason_type = fields.Selection(selection=REASON_TYPE, string='Reason Type', required=1)


class HrChangeControl(models.Model):
    _name = 'hr.change.control'
    _description = "Change Control"
    _inherit = 'mail.thread'

    is_change_administrator = fields.Boolean()
    is_massive = fields.Boolean()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    state = fields.Selection(selection=STATE_TYPE_CHANGE, string='state', default='draft', copy=False)

    """General Fields"""
    name = fields.Char('Reference', copy=False)
    motive_change_id = fields.Many2one('hr.motivos.ccambios', 'Motive')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    creation_date = fields.Date('Creation Date', default=date.today(), copy=False)
    validation_date = fields.Date('Validation Date', copy=False)
    rrhh_manager_id = fields.Many2one('hr.employee', 'RRHH Manager')
    description = fields.Text('Description', copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contract')

    """Salary Change"""
    type_change = fields.Selection(selection=TYPE_CHANGE, string='Type Change')
    is_change_percentage = fields.Boolean('Percentage Change')
    percentage = fields.Float('Percentage')
    previous_salary = fields.Monetary('Previous Salary')
    new_salary = fields.Monetary('New Salary')

    """Administrator Change"""
    type_change_administrator = fields.Selection(selection=TYPE_CHANGE_ADMINISTRATOR, string='Type Change')
    new_administrator_id = fields.Many2one('res.partner', 'New Administrator')
    previous_administrator_id = fields.Many2one('res.partner', 'Previous Administrator')

    """Massive"""
    lines_ids = fields.One2many('hr.salary.change.lines', 'change_control_id')

    @api.onchange('contract_id')
    def _calculate_previous_salary(self):
        if self.contract_id:
            self.previous_salary = self.contract_id.wage

    @api.onchange('employee_id')
    def _get_contract(self):
        if self.employee_id and not self.is_massive:
            contract = self.env['hr.contract'].search(
                [('state', '=', 'open'), ('employee_id', '=', self.employee_id.id)], limit=1)
            if contract:
                self.contract_id = contract

    @api.onchange('type_change_administrator')
    def onchange_domain_type_change_administrator(self):
        if self.type_change_administrator:
            domain = {}
            if self.type_change_administrator == 'is_eps':
                domain = {'domain': {'new_administrator_id': [('check_eps', '=', True)]}}

            if self.type_change_administrator == 'is_arl':
                domain = {'domain': {'new_administrator_id': [('check_arl', '=', True)]}}

            if self.type_change_administrator == 'is_ccf':
                domain = {'domain': {'new_administrator_id': [('check_ccf', '=', True)]}}

            if self.type_change_administrator == 'pension_found':
                domain = {'domain': {'new_administrator_id': [('check_afp', '=', True)]}}

            if self.type_change_administrator == 'cesantia_fund':
                domain = {'domain': {'new_administrator_id': [('check_afp', '=', True)]}}

            return domain

    @api.onchange('is_change_administrator')
    def change_domain_motive_change_id(self):
        if self.is_change_administrator:
            return {'domain': {'motive_change_id': [('reason_type', '=', 'change_administrator')]}}

        return {'domain': {'motive_change_id': [('reason_type', '=', 'salary_change')]}}

    """Button Methods"""

    def confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def validate(self):
        self.validation_date = date.today()

        if self.is_change_administrator:
            if self.is_massive:
                for line in self.lines_ids:
                    if self.type_change_administrator == 'is_eps':
                        line.contract_id.write({
                            'eps_id': self.new_administrator_id.id
                        })

                    if self.type_change_administrator == 'is_arl':
                        line.contract_id.write({
                            'arl_id': self.new_administrator_id.id
                        })

                    if self.type_change_administrator == 'is_ccf':
                        line.contract_id.write({
                            'ccf_id': self.new_administrator_id.id
                        })

                    if self.type_change_administrator == 'pension_found':
                        line.contract_id.write({
                            'pension_fund_id': self.new_administrator_id.id
                        })

                    if self.type_change_administrator == 'cesantia_fund':
                        line.contract_id.write({
                            'cesantia_fund_id': self.new_administrator_id.id
                        })

                    vals = {
                        'type_change_administrator': self.type_change_administrator,
                        'motive_change_id': self.motive_change_id.id,
                        'employee_id': line.employee_id.id,
                        'new_administrator_id': self.new_administrator_id.id,
                        'previous_administrator_id': line.previous_administrator_id.id,
                        'contract_id': line.contract_id.id,
                        'creation_date': self.creation_date,
                        'validation_date': self.validation_date,
                        'rrhh_manager_id': self.rrhh_manager_id.id,
                        'is_change_administrator': True,
                        'is_massive': False,
                        'state': 'validated',
                    }
                    self.env['hr.change.control'].create(vals)

            else:
                if self.type_change_administrator == 'is_eps':
                    self.contract_id.write({
                        'eps_id': self.new_administrator_id.id
                    })

                if self.type_change_administrator == 'is_arl':
                    self.contract_id.write({
                        'arl_id': self.new_administrator_id.id
                    })

                if self.type_change_administrator == 'is_ccf':
                    self.contract_id.write({
                        'ccf_id': self.new_administrator_id.id
                    })

                if self.type_change_administrator == 'pension_found':
                    self.contract_id.write({
                        'pension_fund_id': self.new_administrator_id.id
                    })

                if self.type_change_administrator == 'cesantia_fund':
                    self.contract_id.write({
                        'cesantia_fund_id': self.new_administrator_id.id
                    })

        else:
            if self.is_massive:
                for line in self.lines_ids:
                    line.contract_id.write({
                        'wage': line.new_salary
                    })
                    vals = {
                        'type_change': self.type_change,
                        'motive_change_id': self.motive_change_id.id,
                        'previous_salary': line.previous_salary,
                        'contract_id': line.contract_id.id,
                        'new_salary': line.new_salary,
                        'validation_date': self.validation_date,
                        'rrhh_manager_id': self.rrhh_manager_id.id,
                        'employee_id': line.employee_id.id,
                        'is_massive': False,
                        'is_change_administrator': False,
                        'state': 'validated',
                    }
                    self.env['hr.change.control'].create(vals)

            else:
                if self.is_change_percentage:
                    new_salary = self.contract_id.wage + ((self.contract_id.wage * self.percentage) / 100)
                else:
                    new_salary = self.new_salary
                self.contract_id.write({
                    'wage': new_salary
                })

        self.state = 'validated'

    def cancel(self):
        for rec in self:
            rec.state = 'canceled'

    def go_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    """Inherit Methods"""

    @api.model
    def create(self, vals):

        concept = super(HrChangeControl, self).create(vals)

        if not concept.name:
            if concept.is_change_administrator and concept.is_massive:
                number = self.env['ir.sequence'].next_by_code('hr.change.administrator',
                                                              sequence_date=concept.creation_date)

            if not concept.is_change_administrator and concept.is_massive:
                number = self.env['ir.sequence'].next_by_code('hr.change.salary', sequence_date=concept.creation_date)

            if concept.is_change_administrator and not concept.is_massive:
                number = self.env['ir.sequence'].next_by_code('hr.change.administrator.single',
                                                              sequence_date=concept.creation_date)

            if not concept.is_change_administrator and not concept.is_massive:
                number = self.env['ir.sequence'].next_by_code('hr.change.salary.single',
                                                              sequence_date=concept.creation_date)

            concept.write({
                'name': number
            })

        return concept


class HrEmployeeChangeLines(models.Model):
    _name = 'hr.salary.change.lines'
    _description = 'Salary Change Lines'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    change_control_id = fields.Many2one('hr.change.control')

    contract_id = fields.Many2one('hr.contract', 'Contract Reference')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    identification_id = fields.Char('Identification No', related='employee_id.identification_id')
    previous_salary = fields.Monetary('Previous Salary')
    new_salary = fields.Monetary('New Salary')
    previous_administrator_id = fields.Many2one('res.partner')
    new_administrator_id = fields.Many2one('res.partner', related='change_control_id.new_administrator_id')
    type_change_administrator = fields.Selection(selection=TYPE_CHANGE_ADMINISTRATOR, string='Type Change',
                                                 related='change_control_id.type_change_administrator')

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def _get_contract(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('state', '=', 'open'), ('employee_id', '=', self.employee_id.id)], limit=1)
            if contract:
                self.contract_id = contract
            if self.change_control_id.is_change_percentage:
                self.new_salary = self.contract_id.wage + (
                        (self.contract_id.wage * self.change_control_id.percentage) / 100)

    @api.depends('employee_id')
    @api.onchange('contract_id')
    def _calculate_previous_salary(self):
        if self.contract_id:
            self.previous_salary = self.contract_id.wage

    @api.depends('employee_id')
    @api.onchange('contract_id')
    def _calculate_previous_administrator(self):
        if self.employee_id:
            domain = {}
            if self.change_control_id.type_change_administrator == 'is_eps':
                self.previous_administrator_id = self.contract_id.eps_id
                domain = {'domain': {'new_administrator_id': [('check_eps', '=', True)]}}

            if self.change_control_id.type_change_administrator == 'is_arl':
                self.previous_administrator_id = self.contract_id.arl_id
                domain = {'domain': {'new_administrator_id': [('check_arl', '=', True)]}}

            if self.change_control_id.type_change_administrator == 'is_ccf':
                self.previous_administrator_id = self.contract_id.ccf_id
                domain = {'domain': {'new_administrator_id': [('check_ccf', '=', True)]}}

            if self.change_control_id.type_change_administrator == 'pension_found':
                self.previous_administrator_id = self.contract_id.pension_fund_id
                domain = {'domain': {'new_administrator_id': [('check_afp', '=', True)]}}

            if self.change_control_id.type_change_administrator == 'cesantia_fund':
                self.previous_administrator_id = self.contract_id.cesantia_fund_id
                domain = {'domain': {'new_administrator_id': [('check_afp', '=', True)]}}

            return domain
