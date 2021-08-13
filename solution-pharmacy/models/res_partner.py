# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RestPartnerType(models.Model):
    _inherit = "res.partner"
    _description = "Add customer type field"

    type_client = fields.Selection(String="Type client", 
                                   selection=[('specialist', 'Specialist'), ('distributor', 'Distributor'), ('patient', 'Patient')],
                                   requeried=True,
                                   store=True)
    
