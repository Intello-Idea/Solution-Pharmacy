# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, _, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one('res.partner', string="Asociado")
    military_card_number = fields.Integer(string='Numero de tarjeta militar')
    military_category = fields.Char(string='Categoria Militar')
    military_district = fields.Char(string='Distrito Militar')
    blood_type = fields.Char(string='Grupo Sanguíneo')
    rh = fields.Char(string='RH')
    fam_ids = fields.One2many('hr.employee.family', 'employee_id', string='Familia')
    endowment_ids = fields.One2many('hr.employee.endowment', 'employee_id', string='Dotación')
    resource_calendar_holidays_id = fields.Many2one('resource.calendar', string='Calendario festivo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]" )

