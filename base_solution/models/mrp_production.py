# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    grams_pharmaceutical = fields.Float(String="Grams Pharmaceutical", digits='Product Unit of Measure', compute="_grams_pharmaceutical")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form", compute="_grams_pharmaceutical")

    @api.depends("origin")
    def _grams_pharmaceutical(self):
        result_query = self.env['sale.order'].search([ '&', ('name', '=', self.origin), ('order_line.product_id.name', '=', 'Generico cotizador')]).order_line
        if result_query:
            self.pharmaceutical_form = result_query['pharmaceutical_form']
            self.grams_pharmaceutical = result_query['grams_pharmaceutical']
        else:
            self.pharmaceutical_form = self.bom_id.pharmaceutical_id.id
            self.grams_pharmaceutical = self.bom_id.grams_pharmaceutical