# -*- coding: utf-8 -*-

from odoo import models, fields
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    raw_material = fields.One2many('raw.material', 'sale_order', string="Material")

#    def action_confirm(self):
#        res = super(SaleOrder, self).action_confirm()
#        
#        for line in self:
#            values = []
#            for record in self.raw_material:
#                dic = {
#                    'product_id': record.product_id.id,
#                    'product_uom_qty': record.product_qty,
#                    'product_uom': 1
#                }
#                values.append((0,0,dic))
#            vals = {
#                'move_raw_ids': values,
#            }
#        self.env['sale.order'].write(vals)
#        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form")
    
class SaleOrderRaw(models.Model):
    _name = "raw.material"
    _description = "Lista de materiales"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    percentage = fields.Float(string="Percentage(%)")
    price_unit = fields.Float('Unit Price', digits='Product Unit of Measure')
    price_total = fields.Float('Subtotal price', digits='Product Unit of Measure')
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id", store=True)
    category = fields.Char(string="Categoria", related="product_id.categ_id.complete_name")
    sale_order = fields.Many2one('sale.order', 'Raw material')