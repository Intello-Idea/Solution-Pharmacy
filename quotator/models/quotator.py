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
    product_qty = fields.Integer(string="Quantity", default=1.0, readonly="True")
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    user = fields.Many2one('res.users', string='Quotator', required=True, readonly=True, default=lambda self: self.env.user)
    quotator_date = fields.Date(string="Quotation date", readonly=True, index=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Expiration date", required=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", related="partner_id.property_product_pricelist", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    patient = fields.Char(string="Patient")
    pharmaceutical_form = fields.Many2one('pharmaceutical.form', string="Pharmaceutical form", required=True)
    quotator_lines = fields.One2many('quotator.lines', 'quotator_id', string="Materials")
    subtotal_grams = fields.Integer(string="subtotal size(gr)", required=True, default=1.0)
    total_grams = fields.Integer(string="Total size(gr)", compute="_compute_size_total", store=True)
    value_pharmaceutical_form = fields.Float(string="size(g) pharmaceutical form", compute="_compute_subtotal_pharmaceutical", store=True)
    total_pharmaceutical_form = fields.Float(string="Total", compute="_compute_total_pharmaceutical", store=True)
    total = fields.Float(string="Total", compute="_compute_total_quotator")
    medical_formula = fields.Binary('Medical formula', required=True)
    presentation_id = fields.Many2one('pharmaceutical.presentation', string='Farmaceutical presentation')
    line_production_id = fields.Many2one('production.lines', string="Production Lines")
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
            raise ValidationError(_('The percentages are not correct'))   
        else:
            self.value_pharmaceutical_form = (self.total_grams - suma)
    
    @api.onchange('quotator_lines', 'subtotal_grams')
    def _clean_raw_materia(self):
        if self.pricelist_id.name in ('Tarifa Especialista', 'Tarifa Distribuidor', 'Tarifa Paciente', 'Tarifa Empleado'):
            if self.subtotal_grams <= 0 or self.subtotal_grams > 1000:
                self.quotator_lines = False
                return {
                    'warning':{
                        'title': "Valores incorrectos",
                        'message': "La cantidad de gramos por producto no es correcta, cámbiela",
                    },
                }

    # Tarifa de precios para calcular el valor total del producto final 
    def _compute_price_total_product_final(self, price_x_unit, total_price, category, qty, size_subtotal):
        price_total = 0
        if category == 'Tarifa Especialista':
            if size_subtotal <= 15:
                if price_x_unit < 12000:
                    price_total = 12000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 16 and size_subtotal <= 40:
                if price_x_unit < 14000:
                    price_total = 14000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 41 and size_subtotal <= 80:
                if price_x_unit < 18000:
                    price_total = 18000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 81 and size_subtotal <= 120:
                if price_x_unit < 21000:
                    price_total = 21000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 121 and size_subtotal <= 180:
                if price_x_unit < 24000:
                    price_total = 24000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 181 and size_subtotal <= 220:
                if price_x_unit < 27000:
                    price_total = 27000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 221 and size_subtotal <= 280:
                if price_x_unit < 30000:
                    price_total = 30000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 281 and size_subtotal <= 350:
                if price_x_unit < 34000:
                    price_total = 34000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 351 and size_subtotal <= 450:
                if price_x_unit < 36000:
                    price_total = 36000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 451 and size_subtotal <= 600:
                if price_x_unit < 39000:
                    price_total = 39000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 601 and size_subtotal <= 800:
                if price_x_unit < 42000:
                    price_total = 42000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 801 and size_subtotal <= 1000:
                if price_x_unit < 45000:
                    price_total = 45000*qty
                else:
                    price_total = total_price
        if category == 'Tarifa Distribuidor':
            if size_subtotal <= 15:
                if price_x_unit < 10000:
                    price_total = 10000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 16 and size_subtotal <= 40:
                if price_x_unit < 12000:
                    price_total = 12000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 41 and size_subtotal <= 80:
                if price_x_unit < 15000:
                    price_total = 15000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 81 and size_subtotal <= 120:
                if price_x_unit < 18000:
                    price_total = 18000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 121 and size_subtotal <= 180:
                if price_x_unit < 20000:
                    price_total = 20000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 181 and size_subtotal <= 220:
                if price_x_unit < 23000:
                    price_total = 23000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 221 and size_subtotal <= 280:
                if price_x_unit < 25000:
                    price_total = 25000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 281 and size_subtotal <= 350:
                if price_x_unit < 29000:
                    price_total = 29000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 351 and size_subtotal <= 450:
                if price_x_unit < 31000:
                    price_total = 31000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 451 and size_subtotal <= 600:
                if price_x_unit < 33000:
                    price_total = 33000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 601 and size_subtotal <= 800:
                if price_x_unit < 36000:
                    price_total = 36000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 801 and size_subtotal <= 1000:
                if price_x_unit < 38000:
                    price_total = 38000*qty
                else:
                    price_total = total_price
        if category == 'Tarifa Paciente':
            if size_subtotal <= 15:
                if price_x_unit < 30000:
                    price_total = 30000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 16 and size_subtotal <= 40:
                if price_x_unit < 35000:
                    price_total = 35000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 41 and size_subtotal <= 80:
                if price_x_unit < 45000:
                    price_total = 45000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 81 and size_subtotal <= 120:
                if price_x_unit < 52000:
                    price_total = 52000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 121 and size_subtotal <= 180:
                if price_x_unit < 60000:
                    price_total = 60000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 181 and size_subtotal <= 220:
                if price_x_unit < 68000:
                    price_total = 68000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 221 and size_subtotal <= 280:
                if price_x_unit < 75000:
                    price_total = 75000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 281 and size_subtotal <= 350:
                if price_x_unit < 85000:
                    price_total = 85000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 351 and size_subtotal <= 450:
                if price_x_unit < 90000:
                    price_total = 90000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 451 and size_subtotal <= 600:
                if price_x_unit < 98000:
                    price_total = 98000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 601 and size_subtotal <= 800:
                if price_x_unit < 105000:
                    price_total = 105000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 801 and size_subtotal <= 1000:
                if price_x_unit < 115000:
                    price_total = 115000*qty
                else:
                    price_total = total_price
        if category == 'Tarifa Empleado':
            if size_subtotal <= 15:
                if price_x_unit < 8000:
                    price_total = 8000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 16 and size_subtotal <= 40:
                if price_x_unit < 9000:
                    price_total = 9000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 41 and size_subtotal <= 80:
                if price_x_unit < 11000:
                    price_total = 11000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 81 and size_subtotal <= 120:
                if price_x_unit < 13000:
                    price_total = 13000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 121 and size_subtotal <= 180:
                if price_x_unit < 14000:
                    price_total = 14000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 181 and size_subtotal <= 220:
                if price_x_unit < 16000:
                    price_total = 16000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 221 and size_subtotal <= 280:
                if price_x_unit < 17000:
                    price_total = 17000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 281 and size_subtotal <= 350:
                if price_x_unit < 19000:
                    price_total = 19000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 351 and size_subtotal <= 450:
                if price_x_unit < 20000:
                    price_total = 20000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 451 and size_subtotal <= 600:
                if price_x_unit < 22000:
                    price_total = 22000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 601 and size_subtotal <= 800:
                if price_x_unit < 23000:
                    price_total = 23000*qty
                else:
                    price_total = total_price
            elif size_subtotal >= 801 and size_subtotal <= 1000:
                if price_x_unit < 25000:
                    price_total = 25000*qty
                else:
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
            raise ValidationError(_("The expiration date cannot be less than the application creation date"))
    
    @api.constrains('quotator_lines')
    def _validar_raw_material(self):
        if not self.quotator_lines:
            raise UserError(_("There are no selected raw materials"))

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
            'grams_pharmaceutical': self.value_pharmaceutical_form,
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
                'medical_formula': self.medical_formula,
                'final_client': self.patient,
            }
        self.env['sale.order'].create(vals)
        self.state = 'posted'
    
    def action_cancel(self):
        self.state = 'cancel'