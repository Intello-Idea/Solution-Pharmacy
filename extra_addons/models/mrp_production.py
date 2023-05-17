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

    @api.model
    def create(self, vls):
        res = super(MrpProduction, self).create(vls)
        if 'origin' in vls:
            stock_move = self.env['sale.order'].search([('name', '=', vls.get('origin'))])
            if stock_move:
                for record in stock_move.order_line:
                    if res.move_dest_ids in record.move_ids:
                        res.homologos = record.product_counterpart.id
        return res