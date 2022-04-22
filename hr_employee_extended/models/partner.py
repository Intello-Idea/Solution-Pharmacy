# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, _, api

class partner(models.Model):
    _inherit = 'res.partner'
    employee_ids = fields.One2many('hr.employee', 'partner_id', string='empleado asociado')