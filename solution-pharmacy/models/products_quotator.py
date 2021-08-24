# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Solution(models.Model):
    _name = "solution.pharmacy.quotator"
    _description = "Solution Pharmacy Quotator"
    _rec_name = "partner_id"

    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotator date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration")
    pharmaceutical_form = fields.Many2one('product.product', string="Pharmaceutical form")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    appointment_lines = fields.One2many('solution.pharmacy.quotator.lines', 'appointment_id', string="Material")
    final_product = fields.One2many('product.lines', 'product_lines', string="Final product")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
        


