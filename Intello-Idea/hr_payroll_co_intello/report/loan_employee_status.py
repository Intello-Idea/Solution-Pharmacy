from odoo import models, fields, exceptions, api


class HrEmployeeLoanStatusReport(models.AbstractModel):
    _name = 'report.hr_payroll_co_intello.loan_employee_status'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Sobreescritura del metodo para validación de contrato activo
        de los empleados a certificar."""

        loans = self.env['hr.employee.loan'].search([('id', 'in', docids)])

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee.loan',
            'loans': loans,
        }