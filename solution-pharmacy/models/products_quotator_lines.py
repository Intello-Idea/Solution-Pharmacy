# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SolutionLines(models.Model):
    _name = "solution.pharmacy.quotator.lines"
    _description = "Solution Pharmacy Quotator Lines"


    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_qty = fields.Integer(string="Quantity", required=True, default=0)
    percentage = fields.Float(string="Percentage(%)", required=True, default=0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    appointment_id = fields.Many2one('solution.pharmacy.quotator', string="Appointment id")
