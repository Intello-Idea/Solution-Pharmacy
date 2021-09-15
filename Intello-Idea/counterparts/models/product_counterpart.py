from odoo import fields, api, models


class ProductCounterpart(models.Model):
    _name = "product.counterpart"
    _description = "product counterpart"

    product_id = fields.Many2one("product.template")
    customer = fields.Many2one("res.partner", string="Customer")
    name = fields.Char(string="Counterpart")

    _sql_constraints = [
        ('id_customer_name_uniq', 'UNIQUE(product_id,customer,name)',
         "¡you cannot have records with the same name and customer in the product!")
    ]
