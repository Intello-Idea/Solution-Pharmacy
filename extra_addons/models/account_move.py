# -*- coding: utf-8 -*-

from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor', related='partner_id.referred_doctor', store=True, readonly=False)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', related='partner_id.team_id')