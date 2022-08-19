# -*- coding: utf-8 -*-

from odoo import fields, models, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operation_type = fields.Many2one('stock.picking.type', string='Operation Type', domain="['|',('name','=','Fabricación I'),('name','=','Fabricación')]")

    @api.onchange('product_tmpl_id')
    def filter_operation_type(self):
        if self.product_tmpl_id.check_status:
            return {'domain': {'operation_type': [('name','=','Fabricación I')]}}
        else:
            return {'domain': {'operation_type': [('name','=','Fabricación')]}}
    
    
