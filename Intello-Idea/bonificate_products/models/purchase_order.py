# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
        

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()

        """
        Compute the amounts of the PO line.
        """
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            for tax in line.taxes_id:
                if line.price_subtotal >= tax.base_value:
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
                else:
                    line.update({
                        'price_tax': 0,
                        'price_total': sum(t.get('amount', 0.0) for t in taxes.get('taxes',0.0)),
                        'price_subtotal': taxes['total_excluded'],
                    })
