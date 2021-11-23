from lxml import etree
import json
from odoo import fields, api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    check_counterpart = fields.Boolean(compute="_check_counterpart")
    product_counterpart = fields.One2many("product.counterpart", "product_id")

    @api.model
    def _check_counterpart(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.counterpart_products')

        if check_status:
            self.check_counterpart = True
        else:
            self.check_counterpart = False
