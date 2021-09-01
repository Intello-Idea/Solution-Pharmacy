# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Solution(models.Model):
    _name = "solution.pharmacy.quotator"
    _description = "Solution Pharmacy Quotator"
    _order = "sequence, id"
    _check_company_auto = True
    
    name = fields.Char('Reference', copy=False, default=lambda self: _('New'), required=True)
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotator date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration")
#    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    appointment_lines = fields.One2many('solution.pharmacy.quotator.lines', 'appointment_id', string="Material")
    final_product = fields.One2many('product.lines', 'final_product_lines', string="Final product")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('solution.pharmacy.quotator') or _('New')
        return super(Solution, self).create(vals)

    @api.onchange('appointment_lines')
    def _compute_subtotal_pharmaceutical(self):
        for line in self.final_product:
            id_product = line._origin.id
            suma = 0.0
            for record in self.appointment_lines:
                if record.final_product_id.id == id_product:
                    suma += record.product_qty
                else:
                    continue
                if suma < line.size_total:
                    line.value_pharmaceutical_form = suma
                else:
                    raise ValidationError(_('Los porcentajes no son los correctos'))


#    @api.onchange('appointment_lines')
#    def _compute_subtotal_pharmaceutical(self):
#        for line in self.final_product:
#            id_product = line._origin.id
#            suma = 0.0
#            for record in self.appointment_lines:
#                if record.final_product_id.id == id_product:
#                    suma += record.percentage
#                else:
#                    continue
#                if suma < 100:
#                    line.value_pharmaceutical_form = suma
#                else:
#                    raise UserError(_("El porcentaje sobrepasa el limite"))
#
#    _sql_constraints = [
#        ('name_uniq', 'unique (name)', '!!! La referencia (Name quotator) ya existe por favor cambiela !!!')
#    ]