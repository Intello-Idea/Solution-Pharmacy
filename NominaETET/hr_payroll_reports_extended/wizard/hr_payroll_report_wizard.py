# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError
import time
from datetime import datetime, timedelta
import xlwt
import base64
# from cStringIO import StringIO
from io import StringIO
from io import BytesIO
import xlsxwriter
import types
import logging

_logger = logging.getLogger(__name__)


class HrPayrollReportWizard(models.TransientModel):
    _name = 'hr.payroll.report.wizard'
    _description = 'Payroll Report Wizard'


    data = fields.Binary("Archivo")
    data_name = fields.Char("nombre del archivo")
    payslip_run_id  = fields.Many2one('hr.payslip.run', 'Payslip run')


    def do_report(self):

        _logger.error("INICIA LA FUNCIÓN GENERAR EL REPORTE ")
        value = self.get_values()
        if not value:
            raise Warning(_('!No hay resultados para los datos seleccionados¡'))
        self.make_file(value)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=hr.payroll.report.wizard&field=data&id=%s&filename=%s' % (self.id, self.data_name),
            'target': 'new',
            'nodestroy': False,
        }
      

    def get_values(self):
        value = []
        # Busca asientos contables 
        if self.payslip_run_id:
            
            self._cr.execute(''' SELECT id, code, name FROM hr_salary_rule WHERE appears_on_payslip is True order by sequence''')
            rules_ids = self._cr.fetchall()
            
            query_header="select pr.name, em.identification_id, em.name, co.date_start, jb.name, co.wage, st.name, cc.name, \
                            ct.acc_number, bk.name"
            query_footer = ' from hr_payslip pa \
                                    left join hr_payslip_run pr on (pr.id=pa.payslip_run_id) \
                                    left join hr_employee em on (em.id=pa.employee_id) \
                                    left join hr_contract co on (co.id=pa.contract_id) \
                                    left join account_analytic_account cc on cc.id=co.analytic_account_id \
                                    left join hr_job jb on (jb.id=em.job_id) \
                                    left join hr_payroll_structure st on (st.id=pa.struct_id) \
                                    left join res_partner_bank ct on (ct.id=em.bank_account_id) \
                                    left join res_bank bk on (bk.id=ct.bank_id)'
            query_where=' where pa.payslip_run_id='+str(self.payslip_run_id.id)
            
            count=1
            query_rule=''
            query_left=''
            line_header='Procesamiento,ID,Nombre,Fecha de ingreso,Cargo,Salario,Estructura salarial,Centro costo,Cuenta bancaria,Banco'
            for rule in rules_ids:
                line_header += ',TOTAL ' + str(rule[2])
                query_rule += ', li' + str(count) + '.total'
                query_left += ' left join hr_payslip_line li' + str(count) + ' on (li' + str(count) + '.slip_id=pa.id and li' + str(count) + '.salary_rule_id=' + str(rule[0]) + ')'
                count+=1
            
            lines=[]
            lines.append(tuple(line_header.split(',')))
            self._cr.execute(query_header+query_rule+query_footer+query_left+query_where)
            lines+=self._cr.fetchall()
                
        return lines


    def make_file(self, value):
        _logger.error("INICIA LA FUNCIÓN CONSTRUIR EL ARCHIVO ")
        buf = BytesIO()
        wb = xlsxwriter.Workbook(buf)
        ws = wb.add_worksheet('Report')        
        
        #formatos
        title_head = wb.add_format({
                        'bold': 1,
                        'border': 0,
                        'align': 'rigth',
                        'valign': 'vcenter'})
        title_head.set_font_name('Arial')
        title_head.set_font_size(10) 
        
        subtitle_head = wb.add_format({
                        'bold': 1,
                        'border': 1,
                        'align': 'rigth',
                        'fg_color': 'orange',
                        'valign': 'vcenter'})
        title_head.set_font_name('Arial')
        title_head.set_font_size(10)
        
        user = self.env['res.users'].browse(self._uid)
        ws.write(0, 0, 'REPORTE DE NOMINA', title_head)
        ws.write(1, 0, str(user.company_id.name), title_head)
        ws.write(2, 0, 'Procesamiento', title_head)
        ws.write(2, 1, str(self.payslip_run_id.name), title_head)
        ws.write(3, 0, 'Fecha Inicio', title_head)
        ws.write(3, 1, str(self.payslip_run_id.date_start), title_head)        
        ws.write(4, 0, 'Fecha Inicio', title_head)
        ws.write(4, 1, str(self.payslip_run_id.date_end), title_head)
        
        fila=6
        for x in value:
            ws.write_row(fila,0,x)
            fila+=1

        try:
            wb.close()
            out = base64.encodestring(buf.getvalue())
            buf.close()
            self.data = out
            self.data_name = 'Reporte inventario' + ".xlsx"
        except ValueError:
            raise Warning('No se pudo generar el archivo')       
#
