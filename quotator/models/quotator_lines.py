# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class QuotatorLine(models.Model):
    _name = "quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    quotator_id = fields.Many2one('quotator.own', string="Quotator id", store=True)
    category = fields.Char(string="Categoria", related="product_id.product_tmpl_id.categ_id.complete_name")
    material_qty = fields.Float(string="Quantity", default=1.0, digits='Product Unit of Measure', compute="_compute_qty", store=True)
    price_unit = fields.Float('Unit Price', required=True, default=0.0, compute="_update_price", store=True)
    price_total = fields.Float('Subtotal price', compute="_compute_price_total", store=True)
    sale_order = fields.Many2one('sale.order', 'Raw material', store=True)

    @api.depends('quotator_id.total_grams', 'percentage')
    def _compute_qty(self):
        for line in self:
            if line.product_id.product_tmpl_id.categ_id.complete_name == 'Materias Primas / Activos':
                line.material_qty = (line.quotator_id.total_grams*line.percentage)/100
    
    @api.depends('quotator_id.pricelist_id', 'product_id')
    def _update_price(self):
        for line in self:
            if not line.quotator_id.pricelist_id:
                raise ValidationError(_('!! No tienes, seleccionado un cliente !!')) 
            else:
                if line.product_id:
                    price = line.quotator_id.pricelist_id.get_product_price(line.product_id, 1.0 or line.material_qty, line.quotator_id.partner_id)
                    if line.product_id.product_tmpl_id.categ_id.complete_name == 'Materias Primas / Activos':
                        line.price_unit = 6 * price
                    if line.product_id.product_tmpl_id.categ_id.complete_name == 'Material Acondicionamiento / Envases / Basico':
                        line.price_unit = 3 * price
                    if line.product_id.product_tmpl_id.categ_id.complete_name == 'Material Acondicionamiento / Envases / Lujo':
                        line.price_unit = 2 * price
                    if line.product_id.product_tmpl_id.categ_id.complete_name in ('Material Acondicionamiento / Etiquetas', 'Material Acondicionamiento / Plegables'):
                        line.price_unit = 2.5 * price
    
    @api.depends('price_unit', 'material_qty')
    def _compute_price_total(self):
        for line in self:
            line.price_total = line.price_unit * line.material_qty