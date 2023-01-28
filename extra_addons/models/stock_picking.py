# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Stockpiking(models.Model):
    _inherit = 'stock.picking'

    def get_production_order(self, line):
        result = ''
        order = self.env['mrp.production'].search([('origin', '=', self.origin),
                                                   ('product_id', '=', line.product_id.id),
                                                   ('state', '=', 'done'),
                                                   ('partner_id', '=', self.partner_id.id)])
        if order:
            if len(order) > 1:
                result = order.filtered(lambda x: x.product_qty == line.quantity_done).name
            else:
                result = order.name

        return result