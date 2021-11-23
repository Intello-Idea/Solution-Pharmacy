from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _compute_active(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.counterpart_products')

        return check_status

    check = fields.Boolean(compute="_compute_active_check", default=_compute_active)

    def _compute_active_check(self):
        parameter = self.env['ir.config_parameter'].sudo()
        check_status = parameter.get_param('res.config.settings.counterpart_products')

        for invoice in self:
            invoice.check = check_status

    @api.onchange('partner_id')
    def _change_customer(self):
        for invoice in self:
            for move in invoice.invoice_line_ids:
                # move.product_counterpart = None
                move.cm_id = invoice.partner_id.id
                move.tm_id = move.product_id.product_tmpl_id.id

    @api.model_create_multi
    def create(self, vals_list):
        return super(AccountMove, self).create(vals_list)

    def write(self, vals):
        return super(AccountMove, self).write(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cm_id = fields.Integer()
    tm_id = fields.Integer()
    product_counterpart = fields.Many2one('product.counterpart',
                                          domain="[('product_id.id','=',tm_id), ('customer.id','=',cm_id)]", store=True)

    # def _get_value_domain(self): Cambia el valor de los campos cm_id, tm_id, product_counterpart
    """@api.depends('product_id')
    def _get_value_domain(self):
        for invoice in self:
            invoice.tm_id = invoice.product_id.product_tmpl_id.id
            invoice.cm_id = invoice.move_id.partner_id.id"""

    @api.onchange('product_id')
    def value_invoice_line(self):
        for invoice in self:
            invoice.tm_id = invoice.product_id.product_tmpl_id.id
            invoice.cm_id = invoice.move_id.partner_id.id

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
