# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    instruction_code = fields.Char(string="Instruction code", related='bom_id.instruction_code', store=True)
    homologos = fields.Many2one('product.counterpart', string="Homologos")
    tm_id = fields.Many2one(related='product_id.product_tmpl_id')

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id, bom_line):
        data = super(MrpProduction, self)._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id,
                                                               bom_line)
        data['fase'] = bom_line.fase
        return data