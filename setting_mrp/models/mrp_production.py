# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import  UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    """Start
        Programmer: Routh Milano
        Date: 26-04-2022
        Requirement: REQ-SP-000007
        Functionality: Agregar campos nuevos para obtener cliente y paciente desde la orden de venta y sino agregar manualmente 
    """
    
    @api.model
    def _get_default_picking_type(self):
        return self.bom_id.operation_type.id
    

    partner_sale_id = fields.Many2one('res.partner', string='Client', related="procurement_group_id.partner_id", store=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    #patient_sale = fields.Many2one('res.partner', string='Patient', related="partner_sale_id", store=True)
    patient = fields.Char(string='Patient', store=True)
    patient_sale = fields.Many2one('res.partner', string='Patient', related="partner_sale_id", store=True)
    bulk_size = fields.Float(string="Bulk Size", compute='_compute_bulk_size', readonly=True, default=[],
                                              copy=False, store=True)
    expiration_date_sp = fields.Date(string="Expiration Date")
    client_code = fields.Char(string='Client Code', related="partner_id.client_code", store=True)
    client_code_sale = fields.Char(string='Client Code', related="partner_sale_id.client_code", store=True)
    
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True, check_company=True)
    

    #Función computada que calcula el tamaño a granel basado en la cantidad a producir por el tamaño
    @api.depends('product_id')
    def _compute_bulk_size(self):
        for mrp_product in self:
            mrp_product.bulk_size = mrp_product.product_uom_qty * mrp_product.size
            print('cantidad')
            print(mrp_product.product_uom_qty)

    #End Programmer: Routh Milano

    def action_draft(self):
        self.update({'state': 'draft'})
        stock_move = self.env['stock.move'].search([('reference', '=', self.name)])
        if len(stock_move):
            for rec in stock_move:
                rec.update({'state':'draft'})
        
    def action_confirm(self):
        self.update({'state': 'confirmed'})
        rec = super(MrpProduction, self).action_confirm()
        return rec
