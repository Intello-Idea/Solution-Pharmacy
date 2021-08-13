# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Solution(models.Model):
    _name = "solution.pharmacy.quatator"
    _description = "Solution Pharmacy Quatator"

    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    type_client = fields.Selection(String="Type client", 
                                   selection=[('specialist', 'Specialist'), ('distributor', 'Distributor'), ('patient', 'Patient')],
                                   required=True)