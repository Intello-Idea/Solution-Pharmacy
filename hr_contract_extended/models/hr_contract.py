# -*- coding: utf-8 -*-


from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Informacion salarial
    retention_method = fields.Selection(string='Metodo de rétencion',
                                        selection=[('NA', 'No aplica'),
                                                   ('M1', 'Metodo 1'),
                                                   ('M2', 'Metodo 2')],
                                        default='NA', required=True)
    integral_salary = fields.Boolean(string="Salario Integral", default=False)

    # Salario Integrado
    salario_integrado = fields.Boolean(string="Salario Integrado", default=False)
    salario_integrado_amount = fields.Float(string="Monto Mensual")

    # Garantizado
    garantizado = fields.Boolean(string="Garantizado", default=False)
    garantizado_amount = fields.Float(string="Monto Mensual")

    # Auxilios
    aux_movilizacion = fields.Boolean(string="Auxilio Movilización", default=False)
    aux_movilizacion_amount = fields.Float(string="Monto Mensual")
    aux_rodamiento = fields.Boolean(string="Auxilio Rodamiento", default=False)
    aux_rodamiento_amount = fields.Float(string="Monto Mensual")
    aux_telefonia = fields.Boolean(string="Auxilio Telefonia", default=False)
    aux_telefonia_amount = fields.Float(string="Monto Mensual")

    # Sena
    sena_stage = fields.Selection([('NA', 'No aplica'), ('E', 'Electiva'), ('P', 'Productiva')], 'Etapa Sena', default='NA')

    causal_termination_id = fields.Many2one('hr.departure.reason', string='Casual de terminacion de contrato')
    risk_id = fields.Many2one('hr.risk', string='Riesgos Laborales')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Activo'),
        ('close', 'Liquidado'),
        ('cancel', 'Liquidado'),
    ], string='Status', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')
    entity_ids = fields.One2many('hr.company.ss', 'contract_id', string='Entidad')
    tag_id = fields.Many2one('account.analytic.tag', string="Etiqueta Analítica")

    @api.onchange('state')
    def _date_end_casual(self):
        for record in self:
            if record.state == 'cancel' and not record.date_end:
               record.date_end = date.today()
