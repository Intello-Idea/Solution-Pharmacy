# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
           
class HrType(models.Model):
    _name = "hr.type"
    _inherit = ['mail.thread']
    _description = "Type"
    _order = "name desc, id desc"


    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency or journal.company_id.currency_id      
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', required=True)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]}, domain=[('type','in',['bank', 'cash']),('recaudo','=',False)])
    type = fields.Selection([('payslip', 'Payslip'),
                              ('liquidation', 'Liquidation'),
                              ('other', 'Other')], 'Type', select=True, required=True)
    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    parent_id = fields.Many2one(related='employee_id.manager_id', string=u"Director", readonly=True, store=True)
    compensation_ids = fields.One2many('hr.compensation.contract', 'contract_id', string='Compensation Contract')

    _sql_constraints = [
        ('ref_unique',
         'UNIQUE(document_type, ref, company_id)',
         "Identification number must be unique!"),
    ]    


    def name_get(self):
        return [(type.id, '%s - %s' % (type.code, type.name)) for type in self]


    @api.one
    @api.constrains('employee_id')
    def get_contract_validacion(self):
        if not self.employee_id.contract_id:
            raise ValidationError('El empleado no tiene un contrato vigente')


    @api.multi
    def advances_confirm(self):
        return self.write({'state': 'confirm'})


    @api.multi
    def onchange_journal_id(self, journal_id=False):
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            return {
                'value': {
                    'currency_id': journal.currency.id or journal.company_id.currency_id.id,
                    'company_id': journal.company_id.id,
                }
            }
        return {}


    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return


    @api.model
    def create(self, vals):
        if not self.env.user.has_group('avoid_cancel_movements.group_manage_wh_location'):
            raise ValidationError(_('You do not have permissions to do this operation'))
        return super(StockLocation, self).create(vals)


    @api.multi
    def write(self, vals):
        if not self.env.user.has_group('avoid_cancel_movements.group_manage_wh_location'):
            raise ValidationError(_('You do not have permissions to do this operation'))
        return super(StockLocation, self).write(vals)        



    ### Wizard desde button
    @api.multi
    def action_validate_AYS_borrador(self):
        view_id = self.env.ref('odoo_module_v8.hr_contract_ARS_borrador_wizard_view').id,
        return {
            'name':_("¿Está seguro?"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hr.contract.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]'
        }