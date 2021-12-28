# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def bonification(self):
        '''Se limpian los registros bonificados cada que se oprimen el boton para no generar duplicidad'''
        delete_bonificate = self.env['sale.order.line'].search([('order_id', '=', self.id), ('bonus', '=', True)])
        delete_bonificate.unlink()
        data = self.env['rate.bonification'].search([('client_type.id', '=', self.partner_id.client_type.id)])
        vls = []
        '''Bucle para obtener los los valores de los rangos y el valor minimo de estos'''
        for line in data.lines_price:
            values = ()
            values = (line.start, line.final, line.quantity_product)
            vls.append(values)
        value_min = min(vls)
        '''Bucle para descartar las lineas que no cumplan el valor minimo que contemplan productos bonificados'''
        result = []
        for record in self.order_line:
            if record.product_uom_qty >= value_min[0]:
                value = ()
                value = (record.product_id.id, record.name, record.product_counterpart.id, record.product_uom_qty)
                result.append(value)
        '''Bucle para la creacion de las lineas de producto a bonificar'''
        bonification = []
        values = []
        for line in result:
            for record in vls:
                if line[3] in range(record[0], record[1]+1):
                    items = {
                            'product_id': line[0],
                            'name': line[1],
                            'product_counterpart': line[2],
                            'product_uom_qty': record[2],
                            'price_unit': 0,
                            'bonus': True,
                        }
                    bonification.append((0,0,items))
        vals = {
                'order_line': bonification,
        }
        record_ids = self.env['sale.order'].search([('name', '=', self.name)])
        for record in record_ids:
            record.update(vals)
#
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bonus = fields.Boolean()