# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = 'mrp.production'

    instruction_code = fields.Char(string="Instruction code", related='bom_id.instruction_code', store=True)