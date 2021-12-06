# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class CrmTeamCategory(models.Model):
    _name = 'crm.team.category'
    _description = 'crm team category'

    category_id = fields.Many2one('product.category','Parent Categories',domain="[('parent_id','=',False)]")
    crm_id = fields.Many2one('crm.team',ondelete='cascade')
    category_value = fields.Float('Category Value')