from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    def default_referred_doctor(self):
        if 'active_model' in self.env.context:
            if self.env.context['active_model'] == 'sale.order':
                order = self.env['sale.order'].search([('id','=',self.env.context['active_id'])])
                return order.referred_doctor.id
        return False
    
    referred_doctor = fields.Many2one('res.partner', string='Referred Doctor', default=default_referred_doctor, domain="[('doctor', '=', True)]")