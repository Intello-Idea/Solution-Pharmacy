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
        if data:
            '''######################################## Bonificaciones para Distribuidores ######################################################'''
            if data.client_type.name == 'Distribuidor':
                result = []
                '''Bucle para descartar todas lineas que no cumplan el valor minimo para asi poder bonificar'''
                for line in self.order_line:
                    if line.product_uom_qty >= data.lines_price['start']:
                        value = ()
                        value = (line.product_id.id, line.name, line.product_counterpart.id, line.product_uom_qty)
                        result.append(value)
                bonification = []
                for record in result:
                    vls = record[3] // data.lines_price['start']
                    items = {
                            'product_id': record[0],
                            'name': record[1],
                            'product_counterpart': record[2],
                            'product_uom_qty': data.lines_price['quantity_product']*vls,
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
            '''######################################## Bonificaciones para Especialistas ######################################################'''
            if data.client_type.name == 'Especialista':
                vls = []
                '''Bucle para obtener los los valores de los rangos y el valor minimo de estos'''
                for line in data.lines_price:
                    values = ()
                    values = (line.start, line.final, line.quantity_product)
                    vls.append(values)
                value_min = min(vls)
                value_max = max(vls)
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
                        if line[3] in range(record[0], record[1]+1) and line[3] < (value_min[0]+value_max[0]):
                            items = {
                                    'product_id': line[0],
                                    'name': line[1],
                                    'product_counterpart': line[2],
                                    'product_uom_qty': record[2],
                                    'price_unit': 0,
                                    'bonus': True,
                                }
                            bonification.append((0,0,items))
                        ''''Se crea este bucle para agregar funcionalidad de cuando pasen el rango maximo
                        si para proximas ocaciones se requiere solo dejar la funcionalidad de los rangos, solo es quitar
                        esta parte del codigo y el en if anterior remover and line[3] < (value_min[0]+value_max[0])'''
                        if line[3] in range(record[0], record[1]+1) and line[3] >= (value_min[0]+value_max[0]):
                            x_round = line[3] // value_max[0]
                            x_residuo = line[3] % value_max[0]
                            residuo = 0
                            for x in vls:
                                if x_residuo in range(x[0], x[1]+1):
                                    residuo = x[2]
                            item2 = {
                                    'product_id': line[0],
                                    'name': line[1],
                                    'product_counterpart': line[2],
                                    'product_uom_qty': (record[2]*x_round)+residuo,
                                    'price_unit': 0,
                                    'bonus': True,
                                }
                            bonification.append((0,0,item2))
                vals = {
                        'order_line': bonification,
                }
                record_ids = self.env['sale.order'].search([('name', '=', self.name)])
                for record in record_ids:
                    record.update(vals)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bonus = fields.Boolean()