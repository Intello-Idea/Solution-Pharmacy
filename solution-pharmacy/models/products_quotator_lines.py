# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SolutionLines(models.Model):
    _name = "solution.pharmacy.quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"
    _rec_name = "product_id"


    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_qty = fields.Float(string="Quantity", default=1.0, digits='Product Unit of Measure', required=True)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    price_unit = fields.Float('Unit Price', required=True, default=0.0, compute="_update_price", store=True)
#    price_subtotal = fields.Float('Subtotal price', compute="_compute_price_subtotal", store=True)
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id", store=True)
    final_product_id = fields.Many2one('product.lines', string="Final product", domain="[('final_product_lines', '=', appointment_id)]") 
#    tax_id = fields.Many2one(
#        'account.tax',
#        domain="[('type_tax_use','=','sale'), ('company_id', '=', company_id)]", check_company=True)

    @api.onchange('final_product_id', 'percentage')
    def _compute_qty(self):
        for line in self:
            line.product_qty = (line.final_product_id.size_total*line.percentage)/100

    def _update_price(self):
        self
        



# Este desarrollo permite recoger el precio unitario de cada product segun la lista de precios 

#    @api.depends('product_id')
#    def _update_price(self):
#        for line in self:
#            if line.product_id:
#                price = line.appointment_id.pricelist_id.get_product_price(line.product_id, 1.0 or line.product_qty, line.appointment_id.partner_id)
#                if price is False:
#                    warning = {
#                        'title': _('No valid pricelist line found.'),
#                        'message':
#                            _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
#                    return {'warning': warning}
#                else:
#                    line.price_unit = price
#    

#    @api.depends('product_id')
#    def _update_price(self):
#        for line in self:
#            line.price_unit = line.product_id.list_price

#    @api.depends('price_unit', 'appointment_id', 'product_qty', 'product_id')
#    def _compute_price_subtotal(self):
#           for line in self:
#               taxes = line.tax_id.compute_all(line.price_unit, line.appointment_id.pricelist_id.currency_id, line.product_qty, line.product_id, line.appointment_id.partner_id)
#               line.price_subtotal = taxes['total_excluded']
                

class Productlines(models.Model):
    _name = "product.lines"
    _description = "Este modelo crea lineas de productos terminados"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Final product", required=True)
    qty = fields.Integer(string="Quantity", default=1.0)
    final_product_lines = fields.Many2one('solution.pharmacy.quotator', string="Final product")
    size_subtotal = fields.Integer(string="subtotal size(gr)", required=True)
    size_total = fields.Integer(string="Total size(gr)", compute="_compute_size_total", store=True)
    pharmaceutical_form = fields.Many2one('product.product', string="Pharmaceutical form", required=True)
    value_pharmaceutical_form = fields.Float(string="size(g) pharmaceutical form")
    price_total = fields.Float(string="Price total")

    @api.depends('size_subtotal', 'qty')
    def _compute_size_total(self):
        for line in self:
            line.size_total = line.qty * line.size_subtotal
        
    