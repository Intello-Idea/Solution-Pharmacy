# -*- coding: utf-8 -*-
from odoo import models, fields

class Quotator(models.Model):
    _inherit = "quotator.own"

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor')