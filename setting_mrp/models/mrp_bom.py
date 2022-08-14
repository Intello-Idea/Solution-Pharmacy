# -*- coding: utf-8 -*-

from odoo import fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operation_type = fields.Many2one('stock.picking.type', string='Operation Type')