# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, _, api

class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Relación", help="Relationship with the employee")
    member_name = fields.Char(string='Nombre Completo')
    member_contact = fields.Char(string='# Contacto')
    birth_date = fields.Date(string="Cumpleaños", tracking=True)


class EmployeeRelationInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.relation'

    name = fields.Char(string="Relationship", help="Relationship with thw employee")
