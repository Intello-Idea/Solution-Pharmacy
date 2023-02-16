# -*- coding: utf-8 -*-

from odoo import fields, models, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operation_type = fields.Many2one('stock.picking.type', string='Operation Type', domain="[('code', '=', 'mrp_operation')]" )

    @api.onchange('production_line_id')
    def filter_operation_typess(self):
        domain = [('')]
        for line in self:
            line.operation_type = False
            if line.production_line_id:
                domain = [('check_status', '=', self.production_line_id.check_status), ('code', '=', 'mrp_operation')]
        return {'domain': {'operation_type': domain}}