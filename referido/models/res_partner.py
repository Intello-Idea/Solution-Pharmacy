# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _

class CustomPartner(models.Model):
    _inherit = 'res.partner'

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor')
    doctor = fields.Boolean(default=False)

    @api.constrains('category_id')
    def category(self):
        for rec in self:
            if rec.category_id != '':
                rec.doctor = False
                for rec_catg in rec.category_id:
                    if rec_catg.name == 'Doctor':
                        rec.doctor = True