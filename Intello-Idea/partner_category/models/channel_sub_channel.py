# -*- coding: utf-8 -*-

from odoo import fields, api
from odoo import models
from odoo import exceptions


class ChannelCategory(models.Model):
    _name = 'channel.category'
    _description = 'Channel Category'

    name = fields.Char(required=True, string='Channel Name')
    code = fields.Char(required=True, string="Code")
    discount = fields.Float(string="Discount")
    sub_channel = fields.One2many('sub.channel.category', 'channel')

    _sql_constraints = [
        ('Type_code', 'UNIQUE (code,name)', '¡you cannot have fields with the same type and code!')]


class SubChannelCategory(models.Model):
    _name = 'sub.channel.category'
    _description = 'Sub Channel Category'

    channel = fields.Many2one('channel.category', relation="sub_channel", column1="id", column2="id")
    name = fields.Char(required=True, string="Sub-Channel Name")
    code = fields.Char(required=True, string="Code")

    _sql_constraints = [
        ('Type_code', 'UNIQUE (code,name)', '¡you cannot have fields with the same type and code!')]
