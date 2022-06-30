# -*- coding: utf-8 -*-

# Start programmer
# Fabian Hernando Vera Carrillo
# 2022-04-18
# Se agrego la validacion de que el campo codigo cliente sea numerico
from odoo import fields, models, api, exceptions
from odoo.tools.translate import _


class CustomPartner(models.Model):
    _inherit = 'res.partner'

    is_provider = fields.Boolean(string='Is provider', default=False)
    is_client = fields.Boolean(string='Is client', default=False)

    # End programmer
    # Fabian Hernando Vera Carrillo
