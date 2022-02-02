# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import models


class ProvideConfiguration(models.Model):
    _name = 'provide.configuration'
    _description = 'Provide Configuration'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code', required=True)

