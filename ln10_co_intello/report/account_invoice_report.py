# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    invoiced_target = fields.Float('Invoiced target',readonly=True)
    category_target_ids = fields.Many2one('product.category','Category',readonly=True)
