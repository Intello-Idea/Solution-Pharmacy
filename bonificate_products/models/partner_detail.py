# -*- coding: utf-8 -*-

from odoo import fields, api
from odoo import models
from odoo import api
from odoo.exceptions import ValidationError


class Details(models.Model):
    _name = 'partner.detail'
    _description = "Partner detail"

    name = fields.Many2one('partner.category', string="Name")
    star_date = fields.Date(string="Date Start", required=True)
    final_date = fields.Date(string="Date Final", required=True)
    unit_purchased = fields.Float(string="Units Purchased", required=True)
    unit_bonus = fields.Float(string="Unit Bonus", required=True)

    @api.constrains('star_date', 'final_date')
    def _test_date(self):
        for date in self:
            if date.star_date > date.final_date:
                raise ValidationError(
                    "La fecha inicial " + str(date.star_date) + " Debe ser mayor a la fecha final " + str(
                        date.final_date))


class PartnerCategory(models.Model):
    _inherit = 'partner.category'

    detail = fields.One2many('partner.detail', 'name')



