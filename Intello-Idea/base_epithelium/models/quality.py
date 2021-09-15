from odoo import api, fields, models
from lxml import etree
import json


class QualityPoint(models.Model):
    _inherit = "quality.point"

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(QualityPoint, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_tmpl_id']"):
            if check_status:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id),('check_status', '=', True)]")
            else:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

        res['arch'] = etree.tostring(doc)

        return res

    @api.onchange('product_tmpl_id')
    def check_invima_change(self):
        if self.product_tmpl_id:
            self.check_status = self.product_tmpl_id.check_status


class QualityCheck(models.Model):
    _inherit = "quality.check"

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(QualityCheck, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_id']"):
            if check_status:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id),('check_status', '=', True)]")
            else:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

        res['arch'] = etree.tostring(doc)

        return res

    @api.onchange('product_id')
    def check_invima_change(self):
        if self.product_id:
            self.check_status = self.product_id.check_status


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    def default_check_status(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        return check_status

    check_status = fields.Boolean('I.', default=default_check_status)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.check_status')

        res = super(QualityAlert, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_tmpl_id']"):
            if check_status:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id),('check_status', '=', True)]")
            else:
                node.set('domain',
                         "[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

        res['arch'] = etree.tostring(doc)

        return res

    @api.onchange('product_tmpl_id')
    def check_invima_change(self):
        if self.product_tmpl_id:
            self.check_status = self.product_tmpl_id.check_status
