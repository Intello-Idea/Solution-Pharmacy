# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_counterpart = fields.Many2one('product.counterpart',
                                          domain="[('product_id.id', '=', tm_id), ('customer.id', '=', cm_id)]",
                                          compute='_compute_prodcut_counterpart')
    
    @api.depends('picking_id.origin')
    def _compute_prodcut_counterpart(self):
        for record in self:
            if record.picking_id.origin != '':
                sale_obj = record.env['sale.order.line'].search([('product_id','=',record.product_id.id),
                ('order_id.name','=',record.picking_id.origin)],limit=1)
                record.product_counterpart = sale_obj.product_counterpart.id
            else:
                record.product_counterpart = False