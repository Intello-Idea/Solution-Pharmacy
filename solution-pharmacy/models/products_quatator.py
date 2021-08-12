# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Solution(models.Model):
    _name = "solution.pharmacy.quatator"
    _description = "Solution Pharmacy Quatator"

    name = fields.Char()