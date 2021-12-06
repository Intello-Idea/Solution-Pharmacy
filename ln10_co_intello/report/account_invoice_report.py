# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    invoiced_target = fields.Float('Invoiced target',readonly=True)
    category_target_ids = fields.Many2one('product.category','Category',readonly=True)
    
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ''',(line.parent_category_id) as category_target_ids,
        (avg(ctc.category_value)) as invoiced_target'''
        
    def _from(self):
        return super(AccountInvoiceReport, self)._from() + "INNER JOIN crm_team_category ctc ON ctc.crm_id = line.team_id AND ctc.category_id = line.parent_category_id"

    def _where(self):
        return super(AccountInvoiceReport, self)._where() + '''
           AND line.price_subtotal != 0
        '''

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ",line.parent_category_id,ctc.category_value"
