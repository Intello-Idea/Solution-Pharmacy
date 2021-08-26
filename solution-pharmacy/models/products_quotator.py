# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Solution(models.Model):
    _name = "solution.pharmacy.quotator"
    _description = "Solution Pharmacy Quotator"
    
    name = fields.Char(string="Name quotator")
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotator date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    appointment_lines = fields.One2many('solution.pharmacy.quotator.lines', 'appointment_id', string="Material")
    final_product = fields.One2many('product.lines', 'final_product_lines', string="Final product")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', '!!! La referencia (Name quotator) ya existe por favor cambiela !!!')
    ]

