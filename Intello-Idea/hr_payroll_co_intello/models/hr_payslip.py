from odoo import api, fields, models

INPUT_TYPE = [('fixed', 'Fixed'), ('news', 'News'), ('loan', 'Loan'), ('expense', 'Expense')]


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payroll_type_id = fields.Many2one('hr.payroll.type', 'Payroll Type')
    payroll_period_id = fields.Many2one('hr.period.lines', 'Payroll Period')
    manage_period = fields.Boolean(related='payroll_type_id.manage_periods')

    @api.onchange('payroll_type_id')
    def _clean_periods(self):
        self.payroll_period_id = None
        self.worked_days_line_ids = None

    def action_payslip_done(self):
        super(HrPayslip, self).action_payslip_done()
        for line in self.input_line_ids:
            if line.origin == 'novelty':
                line.novelty_id.state = 'paid'

    @api.onchange('payroll_period_id')
    def _calculate_date_from_payroll_period(self):
        if self.payroll_period_id:
            self.date_from = self.payroll_period_id.date_from
            self.date_to = self.payroll_period_id.date_to
        else:
            self.date_from = None
            self.date_to = None

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to', 'payroll_type_id')
    def _onchange_employee(self):
        super(HrPayslip, self)._onchange_employee()

        if self.payslip_run_id:
            self.payroll_type_id = self.payslip_run_id.payroll_type_id
            self.payroll_period_id = self.payslip_run_id.payroll_period_id
            self.date_from = self.payslip_run_id.date_start
            self.date_to = self.payslip_run_id.date_end

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        print(self._origin.id)
        input_ids = self._get_input_payslip()
        input_line_ids = self.input_line_ids.browse([])
        for r in input_ids:
            input_line_ids |= input_line_ids.new(r)

        self.input_line_ids = input_line_ids

    def _get_input_payslip(self):
        lines = []

        concept_ids = self.env['hr.concept.fixed'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validated'),
             ('applicable_in', 'in', [self.payroll_type_id.id])])

        novelty_ids = self.env['hr.novelty'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validated'),
             ('applicable_in', 'in', [self.payroll_type_id.id])])

        loan_ids = self.env['hr.employee.loan'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validated'),
             ('applicable_in', 'in', [self.payroll_type_id.id])])

        for loan in loan_ids:
            for line in loan.line_ids:
                if line.state == 'pending':
                    if (line.expiration >= self.date_from and (line.expiration <= self.date_to)):
                        line_loan = {
                            'origin': 'loan',
                            'input_type_id': loan.input_type_id.id,
                            'amount': line.quote_value,
                            'loan_id': line.loan_id.id,
                        }

                        line_loan_interest = {
                            'origin': 'loan',
                            'input_type_id': loan.input_type_id.id,
                            'amount': line.interest,
                            'loan_id': line.loan_id.id,
                        }
                        lines.append(line_loan)
                        lines.append(line_loan_interest)

        for novelty in novelty_ids:
            if novelty.novelty_date >= self.date_from and (novelty.novelty_date <= self.date_to):
                line = {
                    'origin': 'novelty',
                    'input_type_id': novelty.input_type_id.id,
                    'amount': novelty.value,
                    'novelty_id': novelty.id,
                }
                lines.append(line)

        for concept in concept_ids:
            # 1. concept dentro del rango de la nómina
            # 2. concept Inicia antes del inicio de la nómina
            # 2. concept Finaliza después del inicio de la nómina o Después del fin de la nómina
            # 3. concept inicia después del inicio de la nómina
            # 3. concept Finaliza después del fin de la nómina

            if ((self.date_from <= concept.start_date) and (self.date_to >= concept.end_date)) or (
                    (self.date_from <= concept.start_date) and (self.date_to < concept.end_date) and (
                    self.date_to >= concept.start_date)) or (
                    (self.date_from > concept.start_date) and (self.date_to >= concept.end_date) and (
                    self.date_to > concept.start_date) and (self.date_from <= concept.end_date)) or (
                    (self.date_from > concept.start_date) and (self.date_to < concept.end_date)):
                line = {
                    'origin': 'concept',
                    'concept_id': concept.id,
                    'input_type_id': concept.input_type_id.id,
                    'amount': concept.value,
                }
                lines.append(line)

        return lines


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    input_type = fields.Selection(selection=INPUT_TYPE)
    is_active = fields.Boolean('Active', default=False)


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    origin = fields.Selection(selection=[('novelty', 'Novelty'), ('concept', 'Concept'), ('loan', 'Loan')],
                              string='Origin')

    concept_id = fields.Many2one('hr.concept.fixed', 'Concept')
    novelty_id = fields.Many2one('hr.novelty', 'Novelty')
    loan_id = fields.Many2one('hr.employee.loan', 'Loan')
    reference = fields.Char('Reference', compute='_origin_reference')

    def _origin_reference(self):
        for rec in self:
            if rec.origin == 'novelty':
                rec.reference = rec.novelty_id.name

            elif rec.origin == 'concept':
                rec.reference = rec.concept_id.name

            elif rec.origin == 'loan':
                rec.reference = rec.loan_id.name
            else:
                rec.reference = ''


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    payroll_type_id = fields.Many2one('hr.payroll.type', 'Payroll Type')
    payroll_period_id = fields.Many2one('hr.period.lines', 'Payroll Period')
    manage_period = fields.Boolean(related='payroll_type_id.manage_periods')

    @api.onchange('payroll_period_id')
    def _calculate_date_from_payroll_period(self):
        if self.payroll_period_id:
            self.date_start = self.payroll_period_id.date_from
            self.date_end = self.payroll_period_id.date_to
