# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, _, api

class Endowment(models.Model):

    _name = 'hr.endowment'
    _description = 'HR Employee Endowment Color'
    _rec_name = 'description'

    description = fields.Char(string='Descripción')


class EndowmentSize(models.Model):

    _name = 'hr.endowment.size'
    _description = 'HR Employee Endowment Size'
    _rec_name = 'description'

    description = fields.Char(string='Descripción')


class EndowmentColor(models.Model):

    _name = 'hr.endowment.color'
    _description = 'HR Employee Endowment Color'
    _rec_name = 'description'

    description = fields.Char(string='Descripción')


class HrEmployeeEndowment(models.Model):

    _name = 'hr.employee.endowment'
    _description = 'HR Employee Endowment'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee', invisible=1)
    endowment_id = fields.Many2one('hr.endowment', string="Descripción")
    size_id = fields.Many2one('hr.endowment.size', string="Talla")
    color_id = fields.Many2one('hr.endowment.color', string="Color")
    quantity = fields.Integer(string='Cantidad')

