# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Quotator(models.Model):
    _name = "quotator.own"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Solution Pharmacy Quotator"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char('Reference', copy=False, default=lambda self: _('New'), required=True)
    final_product = fields.Char(string="Final product", required=True)
    product_qty = fields.Integer(string="Quantity", default=1.0)
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotator date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration", required=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    patient = fields.Char(string="Patient")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form", required=True)
    quotator_lines = fields.One2many('quotator.lines', 'quotator_id', string="Material")
    subtotal_grams = fields.Integer(string="subtotal size(gr)", required=True, default=1.0)
    total_grams = fields.Integer(string="Total size(gr)", compute="_compute_size_total", store=True)
    value_pharmaceutical_form = fields.Float(string="size(g) pharmaceutical form", compute="_compute_subtotal_pharmaceutical", store=True)
    total_pharmaceutical_form = fields.Float(string="Total", compute="_compute_total_pharmaceutical", store=True)
    total = fields.Float(string="Total", compute="_compute_total_quotator")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('quotator.own') or _('New')
        return super(Quotator, self).create(vals)
    
    @api.depends('subtotal_grams', 'product_qty')
    def _compute_size_total(self):
        for line in self:
            line.total_grams = line.product_qty * line.subtotal_grams

    @api.depends('value_pharmaceutical_form', 'pharmaceutical_form')
    def _compute_total_pharmaceutical(self):
        for line in self:
            line.total_pharmaceutical_form = line.value_pharmaceutical_form * line.pharmaceutical_form.value
##Revisar##
    @api.depends('quotator_lines')
    def _compute_subtotal_pharmaceutical(self):
        suma = 0.0
        for line in self.quotator_lines:
            if line.product_id.categ_id.complete_name == 'Materias Primas / Activos':
                suma += line.material_qty
            else:
                continue
        if suma > self.total_grams: 
            raise ValidationError(_('Los porcentajes no son los correctos'))   
        else:
            self.value_pharmaceutical_form = (self.total_grams - suma)
    
    # Tarifa de precios para calcular el valor total del producto final 
    def _compute_price_total_product_final(self, price_x_unit, total_price, category, qty, size_subtotal):
        price_total = 0
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
        if category == 'Tarifa Empleado':
            price_total = total_price
        return price_total

##Revisar##    
    @api.depends('quotator_lines.price_total', 'total_pharmaceutical_form')
    def _compute_total_quotator(self):
        suma = 0.0
        for record in self.quotator_lines:
            suma += record.price_total

        price_x_unit = (suma+self.total_pharmaceutical_form)/self.product_qty
        category = self.partner_id.property_product_pricelist.name
        total_price = suma+self.total_pharmaceutical_form
        self.total = self._compute_price_total_product_final(price_x_unit,total_price,category,self.product_qty,self.subtotal_grams)

    @api.constrains('quotator_date')
    def _validation_date(self):
        if self.expiration_date < self.quotator_date:
            raise ValidationError(_("La fecha de expiracion no puede ser menor que la fecha de creacion de la solicitud"))
    
    @api.constrains('quotator_lines')
    def _validar_raw_material(self):
        if not self.quotator_lines:
            raise UserError(_("No hay materias primas seleccionadas"))

    def send_quotation(self):
        material = []
        products = []
        product = {
            'product_id': self.env['product.template'].search([('name', '=', 'Generico cotizador')]).id,
            'name': self.final_product,
            'pharmaceutical_form': self.pharmaceutical_form.id,
            'product_uom_qty': self.product_qty,
            'price_unit': self.total/self.product_qty,
            'price_subtotal': self.total,
        }
        products.append((0,0,product))
        for line in self.quotator_lines:
            raw = {
                'product_id': line.product_id.id,
                'product_qty': line.material_qty,
                'percentage': line.percentage,
                'price_unit': 0,
                'appointment_id': line.quotator_id.id,
                'category': line.category,
                'sale_order': line.sale_order,
            }
            material.append((0,0,raw))
        vals = {
                'user_id' : self.user.id,
                'partner_id': self.partner_id.id,
                'date_order': self.quotator_date,
                'validity_date': self.expiration_date,
                'pricelist_id': self.pricelist_id.id,
                'order_line': products,
                'raw_material': material,
            }
        self.env['sale.order'].create(vals)
        self.state = 'posted'
    
    def action_cancel(self):
        self.state = 'cancel'