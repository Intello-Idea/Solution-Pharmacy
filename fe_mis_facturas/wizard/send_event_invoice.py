# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError, UserError


class SendEventInvoiceWizard(models.TransientModel):
    _name = "send.event.invoice.wizard"

    type_claim_event = fields.Selection(string='Tipo de reclamo', selection=[
        ('01', "Documento con inconsistencias"),
        ('02', "Mercancía no entregable totalmente"),
        ('03', "Mercancía no entregable parcialmente"),
        ('04', "Servicio no prestado")
    ], required=True)

    def send(self):
        if not self.type_claim_event:
            raise exceptions.ValidationError("Select type calim event first")
        fe_methods = self.env['fe.mf.methods']
        id = int(self._context['active_id'])
        account_move = self.env['account.move'].search([('id', '=', id)])
        fe_methods.send_event_document(account_move, 3, self.type_claim_event)
        account_move.update({'electronic_document_event_status': '3'})
        # id = int(self._context['active_id'])
        # quotator = self.env['quotator.own'].search([('id', '=', id)])
        # material = []
        # products = []
        # product = {
        #     'product_id': self.env['product.product'].search([('name', '=', 'Generico cotizador')]).id,
        #     'name': quotator.final_product,
        #     'product_uom_qty': quotator.product_qty,
        #     'price_unit': quotator.total / quotator.product_qty,
        #     'price_subtotal': quotator.total,
        #     'default_value': quotator.total,
        # }
        # products.append((0, 0, product))
        # for line in quotator.quotator_lines:
        #     raw = {
        #         'product_id': line.product_id.id,
        #         'product_qty': line.material_qty,
        #         'percentage': line.percentage,
        #         'price_unit': 0,
        #         'appointment_id': line.quotator_id.id,
        #         'category': line.category,
        #         'sale_order': line.sale_order,
        #     }
        #     material.append((0, 0, raw))
        #
        # vals = {
        #     'quotator_reference': quotator.name,
        #     'user_id': quotator.user.id,
        #     'partner_id': quotator.partner_id.id,
        #     'date_order': quotator.quotator_date,
        #     'validity_date': quotator.expiration_date,
        #     'pricelist_id': quotator.partner_id.property_product_pricelist.id,
        #     'order_line': products,
        #     'raw_material': material,
        #     'medical_formula': quotator.medical_formula,
        #     'production_line_id': self.line_production_id.id,
        #     'final_client': quotator.patient,
        #     'form_pharmaceutical': quotator.pharmaceutical_form.id,
        #     'patient': quotator.patient,
        #     'pharmaceutical_presentation': quotator.presentation_id.id,
        #     'grams_pharmaceutical': quotator.value_pharmaceutical_form,
        # }
        # sale_order = self.env['sale.order'].create(vals)
        # quotator.update({'state': 'posted', 'sale_reference': sale_order.name})
