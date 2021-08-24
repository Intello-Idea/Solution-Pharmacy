# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SolutionLines(models.Model):
    _name = "solution.pharmacy.quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"


    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_qty = fields.Float(string="Quantity", default=1.0, digits='Product Unit of Measure', required=True)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    price_unit = fields.Float('Unit Price', required=True, default=0.0, compute="_update_price")
    price_subtotal = fields.Float('Subtotal price', compute="_compute_price_subtotal")
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id")
    tax_id = fields.Many2one(
        'account.tax',
        domain="[('type_tax_use','=','sale'), ('company_id', '=', company_id)]", check_company=True)

    @api.depends('product_id')
    def _update_price(self):
        if self.product_id:
            price = self.appointment_id.pricelist_id.get_product_price(self.product_id, 1.0 or self.product_qty, self.appointment_id.partner_id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price
    
    @api.depends('price_unit', 'appointment_id', 'product_qty', 'product_id')
    def _compute_price_subtotal(self):
           for line in self:
               taxes = line.tax_id.compute_all(line.price_unit, line.appointment_id.pricelist_id.currency_id, line.product_qty, line.product_id, line.appointment_id.partner_id)
               line.price_subtotal = taxes['total_excluded']
    
    @api.onchange('percentage')
    def _compute_qty(self):
        for line in self:
            line.product_qty = line.percentage


class Productlines(models.Model):
    _name = "product.lines"
    _description = "Este modelo crea lineas de productos terminados"

    product_id = fields.Many2one('product.product', string="Final product")
    qty = fields.Integer(string="Quantity")
    product_lines = fields.Many2one('solution.pharmacy.quotator', string="Final product")
    size_subtotal = fields.Integer(string="subtotal size(gr)")
    size_total = fields.Integer(string="Total size(gr)")

    @api.onchange('size_subtotal', 'qty')
    def _compute_size_total(self):
        for line in self:
            line.size_total = line.qty * line.size_subtotal