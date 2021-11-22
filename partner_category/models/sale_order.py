# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo import api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|',('company_id', '=', False), ('company_id', '=', company_id),('bool_bill','=', True)]")
    
    team_id = fields.Many2one(
        'crm.team', 'Sales Team', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", related='partner_invoice_id.team_id', store=True)