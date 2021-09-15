from odoo import api, fields, models, _, exceptions
from datetime import date
from dateutil.relativedelta import relativedelta

INTEREST_TYPE = [('simple', 'Simple'), ('compound', 'Compound'), ('no_applicable', 'Not Applicable')]
FREQUENCY = [('bi_weekly', 'Bi-weekly'), ('monthly', 'Monthly'), ('bimonthly', 'Bimonthly'), ('quarterly', 'Quarterly'),
             ('semiannual', 'Semiannual'), ('annual', 'Annual')]
STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
         ('canceled', 'Canceled'), ('paid', 'Paid')]


class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Hr Employee Loan'
    _inherit = ['mail.thread']

    def _default_name(self):
        name = _('New')
        return name

    state = fields.Selection(STATE, string='state', default='draft')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    name = fields.Char('Reference', default=_default_name, copy=False)

    employee_id = fields.Many2one('hr.employee', 'Employee')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    input_type_id = fields.Many2one('hr.payslip.input.type', 'Loan Type')
    applicable_in = fields.Many2many('hr.payroll.type', string='Applicable In')
    request_date = fields.Date('Request Date')
    approval_date = fields.Date('Approval Date')
    rrhh_manager_id = fields.Many2one('hr.employee', 'RRHH Manager')

    loan_amount = fields.Monetary('Loan Amount')
    quote = fields.Integer('Quotes')
    quote_amount = fields.Integer('Quote Amount')
    interest_type = fields.Selection(INTEREST_TYPE, string='Interest Rate', default='no_applicable')
    interest_rate = fields.Float('Interest Rate (%)')
    interest_input_type_id = fields.Many2one('hr.payslip.input.type', 'Interest Input Type',
                                             domain=[('input_type', '=', 'loan')],
                                             help="Select the entry type for the interest on payroll loans")

    description = fields.Text('Description')
    first_quote_date = fields.Date('First Quote Date')
    frequency_quote = fields.Selection(FREQUENCY, string='Frequency Quote', help="Loan installment cutoff frequency")

    interest_amount = fields.Monetary('Interest Amount', compute='_calculate_interest_amount')
    paid_mount = fields.Monetary('Paid Amount', compute='_calculate_paid_amount')
    total_loan = fields.Monetary('Total Loan', compute='_calculate_summary')
    loan_balance = fields.Monetary('Loan Balance', compute='_calculate_summary')

    line_ids = fields.One2many('hr.employee.loan.line', 'loan_id')

    @api.onchange('interest_type')
    def _clean_interest_rate(self):
        if self.interest_type == 'no_applicable':
            self.interest_rate = 0

    def _calculate_interest_amount(self):
        interest_amount = 0
        for line in self.line_ids:
            interest_amount = interest_amount + line.interest

        self.interest_amount = interest_amount

    def _calculate_paid_amount(self):
        amount_paid = 0
        for line in self.line_ids:
            if line.state == 'paid':
                amount_paid = line.quote_total

        self.paid_mount = amount_paid

    @api.onchange('loan_amount', 'interest_amount', 'paid_mount', 'line_ids')
    def _calculate_summary(self):
        total_loan = self.loan_amount + self.interest_amount
        loan_balance = total_loan - self.paid_mount

        self.total_loan = total_loan
        self.loan_balance = loan_balance

    @api.onchange('loan_amount', 'quote', 'interest_rate')
    def _calculate_quote_amount(self):
        quote_amount = 0
        if self.loan_amount and self.quote:
            quote_amount = self.loan_amount / self.quote

        self.quote_amount = quote_amount

    @api.onchange('employee_id')
    def _get_contract(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('state', '=', 'open'), ('employee_id', '=', self.employee_id.id)], limit=1)
            if contract:
                self.contract_id = contract.id

    def create_dis_aid_line(self, loan_id=False, quote=0, expiration_date=False, quote_value=False, interest=False,
                            quote_total=False, balance=False, state=False):

        return self.env['hr.employee.loan.line'].create(
            {
                'loan_id': loan_id,
                'quote': quote,
                'expiration': expiration_date,
                'quote_value': quote_value,
                'interest': interest,
                'quote_total': quote_total,
                'balance': balance,
                'state': state,
            })

    def _calculate_date_expiration(self, date_start=False, quote=False, expiration_date=False):

        if self.frequency_quote == 'bi_weekly':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(days=15)

        if self.frequency_quote == 'monthly':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(months=1)

        if self.frequency_quote == 'bimonthly':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(months=2)

        if self.frequency_quote == 'quarterly':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(months=3)

        if self.frequency_quote == 'semiannual':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(months=6)

        if self.frequency_quote == 'annual':
            expiration_date = date_start if quote <= 1 else expiration_date + relativedelta(years=1)

        return expiration_date

    """Buttons Methods"""

    def calculate_loan(self):
        for rec in self:
            rec.line_ids.unlink()

            quote = 1
            date_start = self.first_quote_date
            total_balance = self.quote_amount
            expiration_date = False
            interest = 0

            if self.interest_type != 'no_applicable':
                if self.interest_type == 'simple':
                    interest = (self.loan_amount * (self.interest_rate / 100)) / self.quote

            while quote <= self.quote:
                expiration_date = self._calculate_date_expiration(date_start, quote, expiration_date)
                quote_total = self.quote_amount + interest
                balance = self.loan_amount if quote <= 1 else self.loan_amount - total_balance

                if balance < 100:
                    quote_total = round(quote_total + balance)
                    balance = 0

                line = rec.create_dis_aid_line(
                    loan_id=self.id,
                    quote=quote,
                    expiration_date=expiration_date,
                    quote_value=rec.quote_amount,
                    interest=interest,
                    quote_total=quote_total,
                    balance=balance,
                    state='draft',
                )
                total_balance = total_balance + rec.quote_amount
                expiration_date = expiration_date
                quote += 1

    def confirm(self):
        if self.line_ids:
            self.state = 'confirmed'

        else:
            raise exceptions.ValidationError(_('The loan must first be calculated and then confirmed.'))

    def validate(self):
        self.state = 'validated'

        for line in self.line_ids:
            line.state = 'pending'

        self.approval_date = date.today()

    def cancel(self):
        self.state = 'canceled'

    """Inherit Methods"""

    @api.model
    def create(self, values):
        loan = super(HrEmployeeLoan, self).create(values)

        if loan.name == _('New'):
            number = self.env['ir.sequence'].next_by_code('hr.employee.loan', sequence_date=loan.request_date)
            loan.write({
                'name': number
            })
        return loan


class HrEmployeeLoanLine(models.Model):
    _name = 'hr.employee.loan.line'
    _description = 'Hr EmployeeLoan Line'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    loan_id = fields.Many2one('hr.employee.loan', 'Loan')
    name = fields.Char('Reference', related='loan_id.name')

    quote = fields.Integer('Quote')
    expiration = fields.Date('Expiration')
    quote_value = fields.Monetary('Quote Value')
    interest = fields.Monetary('Interest')
    quote_total = fields.Monetary('Quote Total')
    balance = fields.Monetary('Balance')

    state = fields.Selection(selection=[('draft', 'Draft'), ('pending', 'Pending'), ('paid', 'Paid')], string="State")


class HrEmployeeLoanConfiguration(models.Model):
    _name = 'hr.employee.loan.configuration'
    _description = 'HrEmployeeLoanConfiguration'

    name = fields.Char()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    accounting_journal_id = fields.Many2one('account.journal', 'Accounting Journal')
    debit_account_id = fields.Many2one('account.account', 'Debit Account')
    credit_account_id = fields.Many2one('account.account', 'Credit Account')
