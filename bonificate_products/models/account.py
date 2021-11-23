from odoo import api, fields, models, _, exceptions


class AccountTax(models.Model):
    _inherit = 'account.tax'

    bonus_tax = fields.Many2one('account.tax', string='Bonus Tax')

    @api.onchange('bonus_tax')
    def _constraint_bonus_tax(self):
        form = self.env['account.tax'].browse(self.ids)
        if self.bonus_tax:
            if self.bonus_tax.id == form.id:
                raise exceptions.ValidationError(_('The bonus tax cannot be equal to the tax'))
