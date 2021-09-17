# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

import logging

_logger = logging.getLogger(__name__)
           
class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'


    def action_generate_report_payroll(self):
        context = dict(self._context or {})
        context = {
            'default_payslip_run_id': self.id,
        } 
        view_id = self.env.ref('hr_payroll_reports_extended.hr_payroll_report_wizard_form').id,
        return {
            'name':_("Generar reporte de nomina"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hr.payroll.report.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }