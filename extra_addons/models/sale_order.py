# -*- coding: utf-8 -*-

from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor', related='partner_id.referred_doctor', store=True)