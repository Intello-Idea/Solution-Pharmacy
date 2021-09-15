from odoo import api, fields, models


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    groups_id = fields.Many2many('res.groups', 'res_groups_server_rel', 'uid', 'gid', string='Groups')