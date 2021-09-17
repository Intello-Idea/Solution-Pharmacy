# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SolutionLines(models.Model):
    _name = "solution.pharmacy.quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"
    _rec_name = "product_id"


    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_qty = fields.Float(string="Quantity", default=1.0, digits='Product Unit of Measure', compute="_compute_qty", store=True)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    price_unit = fields.Float('Unit Price', required=True, default=0.0, compute="_update_price", store=True)
    price_total = fields.Float('Subtotal price', compute="_compute_price_total", store=True)
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id", store=True)
    final_product_id = fields.Many2one('product.lines', string="Final product", domain="[('final_product_lines', '=', appointment_id)]") 
    category = fields.Char(string="Categoria", related="product_id.categ_id.complete_name")

#    tax_id = fields.Many2one(
#        'account.tax',
#        domain="[('type_tax_use','=','sale'), ('company_id', '=', company_id)]", check_company=True)

    @api.depends('final_product_id', 'percentage')
    def _compute_qty(self):
        for line in self:
            if line.product_id.categ_id.complete_name == 'Materias Primas / Activos':
                line.product_qty = (line.final_product_id.size_total*line.percentage)/100


# Este desarrollo permite recoger el precio unitario de cada product segun la lista de precios 

    @api.depends('product_id')
    def _update_price(self):
        for line in self:
            if not line.appointment_id.pricelist_id:
                raise ValidationError(_('!! No tienes, seleccionado un cliente !!')) 
            else:
                if line.product_id:
                    price = line.appointment_id.pricelist_id.get_product_price(line.product_id, 1.0 or line.product_qty, line.appointment_id.partner_id)
                    if line.product_id.categ_id.complete_name == 'Materias Primas / Activos':
                        line.price_unit = 6 * price
                    if line.product_id.categ_id.complete_name == 'Embace Basico':
                        line.price_unit = 3 * price
                    if line.product_id.categ_id.complete_name == 'Embace Embase de Lujo':
                        line.price_unit = 2 * price
                    if line.product_id.categ_id.complete_name == 'Acondicionamiento':
                        line.price_unit = 2.5 * price
    
    @api.depends('price_unit', 'product_qty')
    def _compute_price_total(self):
        for line in self:
            line.price_total = line.price_unit * line.product_qty
        

#    @api.depends('price_unit', 'appointment_id', 'product_qty', 'product_id')
#    def _compute_price_subtotal(self):
#           for line in self:
#               taxes = line.tax_id.compute_all(line.price_unit, line.appointment_id.pricelist_id.currency_id, line.product_qty, line.product_id, line.appointment_id.partner_id)
#               line.price_subtotal = taxes['total_excluded']
                

class Productlines(models.Model):
    _name = "product.lines"
    _description = "Este modelo crea lineas de productos terminados"
    _rec_name = "product_id"

    product_id = fields.Char(string="Final product", required=True)
    qty = fields.Integer(string="Quantity", default=1.0)
    final_product_lines = fields.Many2one('solution.pharmacy.quotator', string="Final product")
    size_subtotal = fields.Integer(string="subtotal size(gr)", required=True, default=1.0)
    size_total = fields.Integer(string="Total size(gr)", compute="_compute_size_total", store=True)
    pharmaceutical_form = fields.Many2one('product.product', string="Pharmaceutical form", required=True)
    value_pharmaceutical_form = fields.Float(string="size(g) pharmaceutical form")
    price_total = fields.Float(string="Total Price", store=True)
    price_unit_pharmaceutical = fields.Float(string="Unit Price", compute="_compute_price_pharmaceutical_form", store=True)
    total_pharmaceutical_form = fields.Float(string="Total", compute="_compute_total_pharmaceutical", store=True)

    @api.depends('size_subtotal', 'qty')
    def _compute_size_total(self):
        for line in self:
            line.size_total = line.qty * line.size_subtotal

    @api.depends('pharmaceutical_form')
    def _compute_price_pharmaceutical_form(self):
        for line in self:
            if line.pharmaceutical_form:
                line.price_unit_pharmaceutical = line.final_product_lines.pricelist_id.get_product_price(line.pharmaceutical_form, 1.0 or line.value_pharmaceutical_form, line.final_product_lines.partner_id)
        
    @api.depends('value_pharmaceutical_form', 'price_unit_pharmaceutical')
    def _compute_total_pharmaceutical(self):
        for line in self:
            line.total_pharmaceutical_form = line.value_pharmaceutical_form * line.price_unit_pharmaceutical
    