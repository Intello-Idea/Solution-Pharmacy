from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    eps_code = fields.Char('EPS Code')
    arl_code = fields.Char('ARL Code')
    ccf_code = fields.Char('CCF Code')
    afp_code = fields.Char('AFP Code')

    """Boolean Fields"""
    is_employee = fields.Boolean('Is Employee?')
    check_eps = fields.Boolean('EPS')
    check_arl = fields.Boolean('ARL')
    check_ccf = fields.Boolean('CCF')
    check_afp = fields.Boolean('AFP')
