# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError


class SendSaleOrderWizard(models.TransientModel):
    _name = "send.sale.order.wizard"

    line_production_id = fields.Many2one('production.lines', required=True)

    """
        Se pasó la función que estaba dentro del modulo de base_solution dentro de quotator.py
        el método se llama send_quotation
    """

    def confirm(self):
        id = int(self._context['active_id'])
        quotator = self.env['quotator.own'].search([('id','=',id)])
        material = []
        products = []
        product = {
            'product_id': self.env['product.product'].search([('name', '=', 'Generico cotizador')]).id,
            'name': quotator.final_product,
            'product_uom_qty': quotator.product_qty,
            'price_unit': quotator.total/quotator.product_qty,
            'price_subtotal': quotator.total,
            'default_value': quotator.total,
        }
        products.append((0, 0, product))
        for line in quotator.quotator_lines:
            raw = {
                'product_id': line.product_id.id,
                'product_qty': line.material_qty,
                'percentage': line.percentage,
                'price_unit': 0,
                'appointment_id': line.quotator_id.id,
                'category': line.category,
                'sale_order': line.sale_order,
            }
            material.append((0, 0, raw))
        
        vals = {
            'quotator_reference': quotator.name,
            'user_id': quotator.user.id,
            'partner_id': quotator.partner_id.id,
            'date_order': quotator.quotator_date,
            'validity_date': quotator.expiration_date,
            'pricelist_id': quotator.partner_id.property_product_pricelist.id,
            'order_line': products,
            'raw_material': material,
            'medical_formula': quotator.medical_formula,
            'production_line_id': self.line_production_id.id,
            'final_client': quotator.patient,
            'form_pharmaceutical': quotator.pharmaceutical_form.id,
            'patient': quotator.patient,
            'pharmaceutical_presentation': quotator.presentation_id.id,
            'grams_pharmaceutical': quotator.value_pharmaceutical_form,
            'user_id': quotator.partner_id.user_id.id,
            'team_id': quotator.partner_id.team_id.id,
        }
        sale_order = self.env['sale.order'].create(vals)
        quotator.update({'state': 'posted', 'sale_reference': sale_order.name})
