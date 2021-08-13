# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Solution(models.Model):
    _name = "solution.pharmacy.quatator"
    _description = "Solution Pharmacy Quatator"
    _rec_name = "partner_id"

    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='User', required=True)
    size = fields.Integer(string="Size", required=True)
    pharmaceutical_form = fields.Integer(string="Farmaceutical form", required=True)
    date = fields.Date(string="Date quatator", readonly=True, index=True, default=fields.Date.context_today)
    term = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)