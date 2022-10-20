from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor')