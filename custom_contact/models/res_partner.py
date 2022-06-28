# -*- coding: utf-8 -*-

# Start programmer
# Fabian Hernando Vera Carrillo
# 2022-04-18
# Se agrego la validacion de que el campo codigo cliente sea numerico
from odoo import fields, models, api, exceptions
from odoo.tools.translate import _



class CustomPartner(models.Model):
    _inherit = 'res.partner'

    client_code = fields.Char(string='Client Code', size=64)
    is_provider = fields.Boolean(string='Is provider', default=False)
    # is_client = fields.Boolean(string='Is client', default=False)
    @api.constrains('client_code')
    def _check_client_code(self):
        for rec in self:
            if rec.client_code != '':
                try:
                    int(rec.client_code)
                except:
                    raise exceptions.Warning(
                        _('Client code must be number'))

    _sql_constraints = [('client_code_uniq','UNIQUE(client_code)',_('Duplicate Client code is not allowed!'))]

    # End programmer
    # Fabian Hernando Vera Carrillo
