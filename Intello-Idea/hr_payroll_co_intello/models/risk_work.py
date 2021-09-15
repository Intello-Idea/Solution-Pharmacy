from odoo import api, fields, models


class HrRiskWork(models.Model):
    _name = 'hr.risk.work'
    _description = 'Clases de riesgo y cotización'

    name = fields.Char(related='risk')
    code = fields.Char('Code')
    risk = fields.Char('Risk')
    risk_class = fields.Char('Class')
    value = fields.Float('Value %', digits=(12, 3))
