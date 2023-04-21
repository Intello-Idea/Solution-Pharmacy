# -*- coding: utf-8 -*-

from odoo import models, api, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_shelf_life = fields.Integer(string="Product shelf life(meses)")