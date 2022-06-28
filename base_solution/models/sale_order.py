# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Se actualiza la funcionalidad del boton confirmar, para que me genere una lista de materiales para un producto generico, dependiendo la cantidad de materias primas
    form_pharmaceutical = fields.Many2one('pharmaceutical.form', string="Form pharmaceutical")
    pharmaceutical_presentation = fields.Many2one('pharmaceutical.presentation', string="Presentation pharmaceutical")
    grams_pharmaceutical = fields.Float(string='grams')

    def action_confirm(self):
        raw = []
        values = []
        index = 0
        res = False
        for prod in self.order_line.product_id:
            if prod.name == 'Generico cotizador':
                for line in self.raw_material:
                    dic = {
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'percent': line.percentage,
                    }
                    raw.append((0,0,dic))
                values = {
                    'pharmaceutical_form': self.form_pharmaceutical.id,
                    'pharmaceutical_presentation': self.pharmaceutical_presentation.id,
                    'size': self.grams_pharmaceutical,
                    'production_line_id': self.production_line_id.id,
                    'product_tmpl_id': self.order_line.product_id[index].product_tmpl_id.id,
                    'bom_line_ids': raw,
                }
                record_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.order_line.product_id[index].product_tmpl_id.id)])

                record = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.order_line[index].product_id.product_tmpl_id.id)]).bom_line_ids.bom_id
                delete = self.env['mrp.bom.line'].search([('bom_id', '=', record._origin.id)])
                delete.unlink()
                for record in record_ids:
                    record.write(values)
                res = super(SaleOrder, self).action_confirm()
            else:
                res = super(SaleOrder, self).action_confirm()
            index += 1
        return res