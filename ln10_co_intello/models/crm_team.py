# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    crm_category_ids = fields.One2many('crm.team.category', 'crm_id', string='')