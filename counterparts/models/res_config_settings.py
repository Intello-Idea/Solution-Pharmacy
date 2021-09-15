from odoo import fields, api, models

import xmltodict
import pprint
import json
import xml.etree.ElementTree as ET


class ResConfigSettingsMod(models.TransientModel):
    _inherit = 'res.config.settings'

    counterpart_products = fields.Boolean(string="Counterpart Products", default=False)

    # set_values,get_values: Guardar el valor del campo counterpart_products
    def set_values(self):
        super(ResConfigSettingsMod, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        select_type.set_param('res.config.settings.counterpart_products', self.counterpart_products)

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsMod, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        sell = select_type.get_param('res.config.settings.counterpart_products')
        res.update({'counterpart_products': sell})
        return res
