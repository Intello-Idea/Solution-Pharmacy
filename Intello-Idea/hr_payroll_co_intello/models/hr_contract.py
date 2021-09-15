from odoo import api, fields, models

CONTRACT_TYPE = [('01', 'Undefined'), ('02', 'Fixed'), ('03', 'Labor Work'), ('04', 'Learning')]
WITHDRAWAL_REASON = [('mutual_agreement', 'Mutual agreement'), ('without_just_cause', 'Without just cause'),
                     ('just_cause', 'Just cause'), ('legal_cause', 'Legal cause')]
PROCEDURE_TYPE = [('p1', 'P1'), ('p2', 'P2')]


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection(CONTRACT_TYPE, 'Contract Type', help='Employee Contract Type')
    identification_id = fields.Char('Identification No', related='employee_id.identification_id')
    eps_id = fields.Many2one('res.partner', 'EPS', domain=[('check_eps', '=', True)], help="Health Care Provider")
    arl_id = fields.Many2one('res.partner', 'ARL', domain=[('check_arl', '=', True)], help='Occupational Risk Manager')
    ccf_id = fields.Many2one('res.partner', 'CCF', domain=[('check_ccf', '=', True)], help='Family Compensation Fund')
    pension_fund_id = fields.Many2one('res.partner', 'Pension Fund', domain=[('check_afp', '=', True)],
                                      help='Pension Fund Administrator')
    cesantia_fund_id = fields.Many2one('res.partner', 'Cesantia Fund', domain=[('check_afp', '=', True)],
                                       help='Cesantia Fund Administrator')
    payment_frequency = fields.Selection(related='structure_type_id.default_schedule_pay', string='Payment Frequency')

    cotizante_type_id = fields.Many2one('hr.cotizante.type', 'Cotizante Type', domain=[('is_active', '=', True)],
                                        help='Type of contributor who pays for the affiliation and is therefore deducted from their salary.')
    cotizante_subtype_id = fields.Many2one('hr.cotizante.subtype', 'Cotizante Subtype')

    risk_work_id = fields.Many2one('hr.risk.work', 'Risk Work')
    risk_class = fields.Char('Risk Class', related='risk_work_id.risk_class')
    risk_percentage = fields.Float('Risk Percentage', related='risk_work_id.value', digits=(12, 3))

    liquidation_date = fields.Date('Liquidation Date')
    withdrawal_reason = fields.Selection(selection=WITHDRAWAL_REASON, string='Withdrawal Reason',
                                         help="Select the reason for termination of the employee's contract")

    procedure_type = fields.Selection(selection=PROCEDURE_TYPE, string='Procedure Type',
                                      help="Type of withholding at the source procedure to be applied on the employee's salary. P1: withholding at source procedure 1. P2: withholding at source procedure 2.")
    prepaid_medicine = fields.Monetary('Prepaid Medicine', help='Prepaid medicine monthly value')
    deduction_housing = fields.Monetary('Deduction for Housing', help='Interest on home loans monthly value')
    voluntary_pension_contribution = fields.Monetary('Voluntary Pension Contribution',
                                                     help='Voluntary pension contribution (exempt income) monthly amount ')
    voluntary_afc_contribution = fields.Monetary('Voluntary AFC Contribution',
                                                 help="Voluntary savings contribution for the promotion of construction (AFC), which is not part of the taxpayer's withholding tax base and is income exempt from income tax and complementary taxes. Monthly contribution amount")
    dependents = fields.Monetary('Dependents', help='Amount dependent on the taxpayer')

    integral_salary = fields.Boolean('Integral Salary', default=False)

    control_salary_change_ids = fields.One2many('hr.change.control', 'contract_id',
                                                domain=[('is_change_administrator', '=', False),
                                                        ('is_massive', '=', False)])
    control_administrator_change_ids = fields.One2many('hr.change.control', 'contract_id',
                                                       domain=[('is_change_administrator', '=', True),
                                                               ('is_massive', '=',False)])
    """Inherit Fields"""
    name = fields.Char(required=False)
    structure_type_id = fields.Many2one('hr.payroll.structure.type', 'Salary Structure')

    @api.model
    def create(self, vals):
        contract = super(HrContract, self).create(vals)
        contract.create_contract_ref()

        return contract

    def create_contract_ref(self):
        if self.employee_id:
            contract_ex = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('id', '!=', self.id)])
            range_zero = '00'
            contracts = len(contract_ex)
            if contract_ex:
                if contracts >= 9:
                    range_zero = '0'
                elif contracts >= 99:
                    range_zero = ''
                self.name = str(self.employee_id.identification_id) + '-' + 'C' + str(range_zero) + str(
                    contracts + 1)
            else:
                self.name = str(self.employee_id.identification_id) + '-' + 'C' + str(range_zero) + str(1)

    """Onchange Methods"""

    @api.onchange('cotizante_type_id')
    def onchange_cotizante_type(self):
        if self.cotizante_type_id:
            self.cotizante_subtype_id = False


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    """Inherit Fields"""
    default_schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Biweekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Default Scheduled Pay', default='monthly',
        help="Defines the frequency of the wage payment.")
