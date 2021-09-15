# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo import api
from odoo.exceptions import ValidationError


class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    classification = fields.Text(string='Classification', compute="_calculate_code", store=True)
    name = fields.Char(string='Name', required=True)
    payment_deadline = fields.Many2one('account.payment.term', string='Payment deadline')
    channel = fields.Many2one('channel.category', string='Channel')
    sub_channel = fields.Many2one('sub.channel.category', string='Sub Channel', domain="[('channel', '=', channel)]")
    by_product = fields.Boolean('Bonificate Product')

    _sql_constraints = [
        ('Channel_Sub-channel_unique', 'UNIQUE (channel,sub_channel)', '!')
    ]

    @api.depends('channel', 'sub_channel')
    def _calculate_code(self):
        for rec in self:
            rec.classification = str(rec.channel.code) + str(rec.sub_channel.code)

    @api.constrains('name')
    def _name_constrains(self):
        if len(self.name) < 6:
            raise ValidationError("El nombre debe tener minimo 6 caracteres")


class Partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model
    supplier_category = fields.Many2one('provide.configuration', string='Provider Code')
    zones_channels = fields.Many2one('partner.category', string="Client Category")
    sub_channel = fields.Integer(related='zones_channels.sub_channel.id', readonly=True)
    channel = fields.Integer(related='zones_channels.channel.id', readonly=True)
    code_channel = fields.Text(string="Classification", compute="_compute_classification")
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
    def _compute_classification(self):
        self.code_channel = self.zones_channels.classification

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

    # Customer field of many to many to the res.partner model
    client = fields.Many2many('res.partner', column1="id", column2="res_partner_id", string="Client")
    partner_categorys_ids = fields.Many2many('partner.category')
    star_date = fields.Date(string='Date Start')
    final_date = fields.Date(string='Date Final')
    classification = fields.Text(string="Classification", compute="_compute_code", store=True)
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

    @api.depends('partner_categorys_ids')
    def _compute_code(self):
        cha = self.partner_categorys_ids
        accum = " "
        for channel in cha:
            accum = accum + str(channel.classification) + " - "
        self.classification = accum

    @api.depends('all_channel')
    def _all_to_channel(self):
        if self.all_channel:
            pass