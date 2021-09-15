from odoo import fields, models, api, exceptions
from odoo.tools.translate import _

from xml.etree import ElementTree
import xmltodict
import pprint
import json


class Lead(models.Model):
    _inherit = 'crm.lead'

    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    @api.model
    def filter(self):
        print("_filter_customer")
        form = self.env.ref("base.action_partner_form")
        form.context = "{'res_partner_search_mode': 'customer', 'search_default_customer': 1}"
        print(form.context)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
