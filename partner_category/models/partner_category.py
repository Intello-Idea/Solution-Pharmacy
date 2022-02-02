# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo import api
from odoo.exceptions import ValidationError


class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    name = fields.Char(string='Name', required=True)
    payment_deadline = fields.Many2one('account.payment.term', string='Payment deadline')
    by_product = fields.Boolean('Bonificate Product')

    @api.constrains('name')
    def _name_constrains(self):
        if len(self.name) < 6:
            raise ValidationError("El nombre debe tener minimo 6 caracteres")


class Partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model
    supplier_category = fields.Many2one('provide.configuration', string='Provider Code')
    zones_channels = fields.Many2one('partner.category', string="Client Category")
    payment_deadline = fields.Many2one('account.payment.term', string="Payment deadline", compute="_payment_deadline")
    bool_bill = fields.Boolean('Customer to Bill')
    bool_customer = fields.Boolean('Customer')
    bool_vendor = fields.Boolean('Vendor')

    @api.model
    def default_get(self,vals):
        res = super(Partner,self).default_get(vals)
        res['user_id'] = self.env.user.id
        return res

    @api.depends('zones_channels')
    def _payment_deadline(self):
        self.payment_deadline = self.zones_channels.payment_deadline
    
    @api.onchange('payment_deadline')
    def _onchange_property_payment_term_id(self):
        if self.payment_deadline:
            self.property_payment_term_id = self.payment_deadline.id


class PartnerCanal(models.Model):
    _name = 'partner.channel'
    _description = "Partner Channel"

    name = fields.Char(string='Name', required=True)

    client = fields.Many2many('res.partner', column1="id", column2="res_partner_id", string="Client")
    partner_categorys_ids = fields.Many2many('partner.category')
    star_date = fields.Date(string='Date Start')
    final_date = fields.Date(string='Date Final')
    unit_purchased = fields.Float(string="Unit Purchased")
    unit_bonus = fields.Float(string="Unit Bonus")
    product = fields.Many2one('product.product', string="Product")
    bonificate_product = fields.Boolean('Bonificate same product?')
    bonificate_gift = fields.Boolean('Bonificate gift?')
    discount_bool = fields.Boolean('Discount')
    discount_percentage = fields.Boolean('Discount Percentage')
    percentage = fields.Float('Petcentage')
    discount_value = fields.Boolean('Discount Value')
    value = fields.Float('Value')
    product_bonificate_id = fields.Many2one('product.product', string="Product to Bonificate")
    bonificate_category = fields.Boolean('Bonificate Category active?')

    @api.constrains('unit_purchased', 'unit_bonus')
    def _test_units(self):
        if self.unit_purchased <= 0:
            raise ValidationError("Debes tener al menos una unidad de compra")
        if self.unit_bonus <= 0:
            raise ValidationError("Debes tener al menos una unidad bonificada")

    @api.constrains('star_date', 'final_date')
    def _test_date(self):
        for date in self:
            if date.star_date > date.final_date:
                raise ValidationError(
                    "La fecha inicial " + str(date.star_date) + " No debe ser mayor a la fecha final " + str(
                        date.final_date))