# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Solution(models.Model):
    _name = "solution.pharmacy.quotator"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Solution Pharmacy Quotator"
    _order = "sequence, id"
    _check_company_auto = True
    
    name = fields.Char('Reference', copy=False, default=lambda self: _('New'), required=True)
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotator date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    appointment_lines = fields.One2many('solution.pharmacy.quotator.lines', 'appointment_id', string="Material")
    final_product = fields.One2many('product.lines', 'final_product_lines', string="Final product")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    patient = fields.Char(string="Patient")
    total = fields.Float(string="Total", compute="_compute_total_quotator")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

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
                    if record.product_id.categ_id.complete_name == 'Materias Primas / Activos':
                        suma += record.product_qty
                else:
                    continue
            if suma > line.size_total: 
                raise ValidationError(_('Los porcentajes no son los correctos'))   
            else:
                line.value_pharmaceutical_form = (line.size_total - suma)

# Tarifa de precios para calcular el valor total del producto final 
    def _compute_price_total_product_final(self, price_x_unit, total_price, category, qty, size_subtotal):       
        if category == 'Tarifa Especialista':
            if size_subtotal <= 15:
                if price_x_unit < 12000:
                    price_total = 12000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 30 and size_subtotal <= 40:
                if price_x_unit < 14000:
                    price_total = 14000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 50 and size_subtotal <= 80:
                if price_x_unit < 18000:
                    price_total = 18000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 90 and size_subtotal <= 120:
                if price_x_unit < 21000:
                    price_total = 21000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 150:
                if price_x_unit < 22000:
                    price_total = 22000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 200 and size_subtotal <= 220:
                if price_x_unit < 24000:
                    price_total = 24000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 240 and size_subtotal <= 250:
                if price_x_unit < 25000:
                    price_total = 25000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 300:
                if price_x_unit < 28000:
                    price_total = 28000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 400:
                if price_x_unit < 32000:
                    price_total = 32000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 500:
                if price_x_unit < 34000:
                    price_total = 34000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 1000:
                if price_x_unit < 45000:
                    price_total = 45000*qty
                else:
                    price_total = total_price
            else:
                raise UserError(_('La cantidad de gramos por producto, no es la correcta, por favor cambiarla'))
        if category == 'Tarifa Distribuidor':
            if size_subtotal <= 15:
                if price_x_unit < 10000:
                    price_total = 1000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 30 and size_subtotal <= 40:
                if price_x_unit < 12000:
                    price_total = 12000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 50 and size_subtotal <= 80:
                if price_x_unit < 14000:
                    price_total = 14000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 90 and size_subtotal <= 120:
                if price_x_unit < 16000:
                    price_total = 16000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 150:
                if price_x_unit < 17000:
                    price_total = 17000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 200 and size_subtotal <= 220:
                if price_x_unit < 18000:
                    price_total = 18000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 240 and size_subtotal <= 250:
                if price_x_unit < 19000:
                    price_total = 19000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 300:
                if price_x_unit < 21000:
                    price_total = 21000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 400:
                if price_x_unit < 24000:
                    price_total = 24000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 500:
                if price_x_unit < 26000:
                    price_total = 26000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 1000:
                if price_x_unit < 34000:
                    price_total = 34000*qty
                else:
                    price_total = total_price
            else:
                raise UserError(_('La cantidad de gramos por producto, no es la correcta, por favor cambiarla'))
        if category == 'Tarifa Paciente':
            if size_subtotal <= 15:
                if price_x_unit < 30000:
                    price_total = 3000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 30 and size_subtotal <= 40:
                if price_x_unit < 37000:
                    price_total = 37000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 50 and size_subtotal <= 80:
                if price_x_unit < 45000:
                    price_total = 45000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 90 and size_subtotal <= 120:
                if price_x_unit < 52000:
                    price_total = 52000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 150:
                if price_x_unit < 55000:
                    price_total = 55000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 200 and size_subtotal <= 220:
                if price_x_unit < 60000:
                    price_total = 60000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 240 and size_subtotal <= 250:
                if price_x_unit < 63000:
                    price_total = 63000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 300:
                if price_x_unit < 70000:
                    price_total = 70000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 400:
                if price_x_unit < 80000:
                    price_total = 80000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 500:
                if price_x_unit < 85000:
                    price_total = 85000*qty
                else:
                    price_total = total_price
            elif size_subtotal == 1000:
                if price_x_unit < 115000:
                    price_total = 115000*qty
                else:
                    price_total = total_price
            else:
                raise UserError(_('La cantidad de gramos por producto, no es la correcta, por favor cambiarla'))
        else:
            price_total = total_price
        return price_total
            
    @api.onchange('appointment_lines')
    def _compute_total_product(self):
        for line in self.final_product:
            id_product = line._origin.id
            suma = 0.0
            for record in self.appointment_lines:
                if record.final_product_id.id == id_product:
                    suma += record.price_total
                else:
                    continue
            price_x_unit = (suma+line.total_pharmaceutical_form)/line.qty
            category = self.partner_id.property_product_pricelist.name
            line.price_total = self._compute_price_total_product_final(price_x_unit,(suma+line.total_pharmaceutical_form),category,line.qty,line.size_subtotal)

    @api.depends('appointment_lines')
    def _compute_total_quotator(self):
        suma = 0.0
        for line in self.final_product:
            suma += line.price_total
        self.total = suma

    def send_quotation(self):
        for line in self:
            values = []
            values_raw_material = []
            for record in self.final_product:
                dic = {
                    'product_id': self.env['product.template'].search([('name', '=', 'Generico cotizador')]).id,
                    'name': record.product_id,
                    'pharmaceutical_form': record.pharmaceutical_form.id,
                    'product_uom_qty': record.qty,
                    'price_unit': record.price_total/record.qty,
                    'price_subtotal': record.price_total,
                }
                values.append((0,0,dic))
            for record in self.appointment_lines:
                raw = {
                    'product_id': record.product_id.id,
                    'product_qty': record.product_qty,
                    'percentage': record.percentage,
                    'price_unit': 0,
                    'appointment_id': record.appointment_id.id,
                    'final_product_id': record.final_product_id.id,
                    'category': record.category,
                    'sale_order': record.sale_order,
                }
                values_raw_material.append((0,0,raw))
            vals = {
                'user_id' : line.user.id,
                'partner_id': line.partner_id.id,
                'date_order': line.quotator_date,
                'validity_date': line.expiration_date,
                'pricelist_id': line.pricelist_id.id,
                'order_line': values,
                'raw_material': values_raw_material,
            }
        self.env['sale.order'].create(vals)
        self.state = 'posted'
    
    def action_cancel(self):
        self.state = 'cancel'

    @api.constrains('quotator_date', 'expiration_date')
    def _validation_date(self):
        if self.expiration_date < self.quotator_date:
            raise ValidationError(_("La fecha de expiracion no puede ser menor que la fecha de creacion de la solicitud"))

#    @api.onchange('appointment_lines')
#    def _compute_default_percentage(self):
#        for record in self.appointment_lines:
#            if record.product_id.categ_id.complete_name != 'Materias Primas / Activos':
#                record.percentage = 1

#    @api.onchange("final_product")
#    def compute_product_final(self):
#        vals = []
#        for line in self.final_product:
#            vals.append(line.id)
#        self.provisional = [(6, 0, vals)]

#    _sql_constraints = [
#        ('name_uniq', 'unique (name)', '!!! La referencia (Name quotator) ya existe por favor cambiela !!!')
#    ]