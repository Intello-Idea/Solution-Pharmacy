from odoo import models, fields, api


class ProductFormMagistral(models.Model):
    _name = "product.form.magistral"
    _description = "Product Form Magistral Epithelium"
    _order = "index"

    index = fields.Integer()
    name = fields.Char()
    icon = fields.Binary()
    description = fields.Html()
    color = fields.Char()
    pdf = fields.Binary()
    image_description = fields.Binary()

    _sql_constraints = [('Unique_order', 'UNIQUE(index)', 'No puedes tener dos formulas con el mismo orden')]


