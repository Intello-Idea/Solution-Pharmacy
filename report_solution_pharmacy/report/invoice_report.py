from datetime import timedelta
from odoo import models, fields, api
from odoo.tools.image import image_data_uri
import json


#pip install pymaging-psd
class InvoiceReport(models.AbstractModel):
    _name = 'report.account.report_invoice_with_payments'
    _description = 'Invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        sale_orders = {}
        date = ''
        day = 0
        desc = 0.0
        tax = []
        tax_value = {}
        picking = {}
        qr_code_url = ''

       
        for doc in docs:
            orders = self.env['sale.order'].search([('invoice_ids','=',doc.id),('state', '=', 'done')])
            order = orders[0] if len(orders) == 1 else False
            sale_orders[doc.id] = order

            picking_ref = []
            result = ''
            if orders:
                for line in orders:
                    picking = self.env['stock.picking'].search([('sale_id','=',line.id), ('state', '=', 'done')])
                    for record in picking:
                        picking_ref.append(record.name)

                if picking_ref:
                    result_picking = ''
                    for item in picking_ref:
                        result_picking += item + ', '
                    result = result_picking[:-2]
            
            for rec in doc.invoice_payment_term_id.line_ids:
                day += rec.days
            
            date = doc.invoice_date + timedelta(days=day)

            for rec in doc.invoice_line_ids:
                desc += (rec.discount/100) * rec.price_unit
            
            for rec in doc.amount_by_group:
                tax.append(rec[0])
                tax_value[rec[0]] = rec[3]
           
            if doc.fe_qr_code:
                qr_code_url = doc.build_fe_qr_code()
                
        return {
            'docs': docs,
            'sale_orders': sale_orders,
            'date': date,
            'desc': desc,
            'tax': tax,
            'tax_value': tax_value,
            'picking': result,
            'qr_code_url':qr_code_url
        }