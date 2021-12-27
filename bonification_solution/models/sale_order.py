# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def bonification(self):
        data = self.env['rate.bonification'].search([])
        vals = []
        for line in self.order_line:
            for record in data.lines_price:
                if line.product_uom_qty in range(record['start'], record['final']+1):
                    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:", record.base_price)
                    #values = {
                    #    'product_id': line.product_id.id,
                    #    'name': line.name,
                    #    'product_counterpart': line.product_counterpart.id,
                    #    'price_unit': 0,
                    #    'product_uom_qty': record.base_price,
                    #    'bonus': True,
                    #}
                    #vals.append((0,0,values))
                    #self.env['sale.order.line'].update(values)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bonus = fields.Boolean()