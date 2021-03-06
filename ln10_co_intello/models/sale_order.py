from odoo import models, fields, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        invoice = super(SaleOrder, self)._prepare_invoice()
        invoice.update({
            'from_sale_order': True,
        })
        return invoice

    def action_confirm(self):
        if self.partner_id.quota_client != 0:
            if self.amount_total > self.partner_id.quota_total_remaining:
                raise exceptions.Warning(_('The amount of the sales order completes the client quota'))
        super(SaleOrder, self).action_confirm()
