from odoo import api, fields, models


class StateDocument(models.Model):
    _name = 'fe.state.document'
    _description = 'State Document'

    account_move_id = fields.Many2one('account.move', 'Account Move')
    code = fields.Char('Code')
    description = fields.Char('Description')
