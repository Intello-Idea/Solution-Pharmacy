# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def bonification(self):
        data = self.env['rate.bonification.line'].search([])
        vls = []
        '''Bucle para obtener los los valores de los rangos y el valor minimo de estos'''
        for line in data:
            values = ()
            values = (line.start, line.final)
            vls.append(values)
        value_min = min(vls)
        '''Bucle para descartar las lineas que no cumplan el valor minimo que contemplan productos bonificados'''
        result = []
        for record in self.order_line:
            if record.product_uom_qty >= value_min[0]:
                value = ()
                value = (record.product_id.id, record.product_uom_qty)
                result.append(value)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bonus = fields.Boolean()