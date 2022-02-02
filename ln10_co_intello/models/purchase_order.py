from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    count_invoice = fields.Integer(compute='_compute_count_invoice',copy=False, default=0, store=True)


    @api.depends('order_line.invoice_lines.move_id')
    def _compute_count_invoice(self):
        for record in self:
             invoices = record.order_line.invoice_lines.move_id.filtered(lambda x: x.move_type in ('in_invoice','in_refund'))
             record.count_invoice = len(invoices)
        return invoices

    def view_new_invoices(self):
        invoices = self._compute_count_invoice()
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        result = action
        create_bill = self.env.context.get('create_bill', False)
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        if len(invoices) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(invoices.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            if not create_bill:
                result['res_id'] = invoices.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        return result