from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor')