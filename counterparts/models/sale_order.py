from lxml import etree
import json
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    check_counterpart = fields.Boolean(compute="_compute_active", default=False, store=False)

    @api.onchange('order_line')
    def _compute_active(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.counterpart_products')

        if check_status:
            self.check_counterpart = True
        else:
            self.check_counterpart = False

    @api.onchange('partner_id')
    def _change_customer(self):
        for order in self:
            order.order_line = ()
            order.order_line.cm_id = order.partner_id.id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cm_id = fields.Integer(compute="_get_value_domain")
    tm_id = fields.Integer(compute="_get_value_domain")
    product_counterpart = fields.Many2one('product.counterpart',
                                          domain="[('product_id.id', '=', tm_id), ('customer.id', '=', cm_id)]")

    @api.onchange('product_id')
    def _get_value_domain(self):
        for order_line in self:
            order_line.tm_id = order_line.product_id.product_tmpl_id.id
            order_line.cm_id = order_line.order_id.partner_id.id

    @api.onchange('product_id')
    def value_order_line(self):
        for order_line in self:
            order_line.product_counterpart = ()

    @api.onchange('product_counterpart')
    def value_name(self):
        for line in self:
            if line.product_id:
                code = "[" + str(line.product_id.default_code) + "] "
            else:
                code = ""
            if line.product_counterpart:
                line.name = code + str(line.product_counterpart.name)
            else:
                if line.product_id:
                    line.name = code + str(line.product_id.name)
                else:
                    line.name = None
