# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    raw_material = fields.One2many('stock.raw.material', 'material_stock', string="Raw material")


class StockMaterial(models.Model):
    _name = "stock.raw.material"
    _description = "Almacena las materias primas que se necesitan para cada producto que se envian desde la confirmacion de la cotizacion"

    material_stock = fields.Many2one('stock.picking', string="Stock raw material")
    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    percentage = fields.Float(string="Percentage(%)")