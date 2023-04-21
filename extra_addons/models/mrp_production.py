# -*- coding: utf-8 -*-

from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class MrpBom(models.Model):
    _inherit = 'mrp.production'

    instruction_code = fields.Char(string="Instruction code", related='bom_id.instruction_code', store=True)
    expiration_date_sp = fields.Date(string="Expiration Date",
                                     compute='_calculate_expiration_date',
                                     store=True)

    def _calculate_expiration_date(self):
        for line in self:
            product = line.product_id
            if product:
                product_shelf_life =\
                    product.product_tmpl_id.product_shelf_life
                if product_shelf_life and line.date_planned_start:
                    line.expiration_date_sp = line.date_planned_start +\
                        relativedelta(months=product_shelf_life)
                else:
                    line.expiration_date_sp = line.date_planned_start