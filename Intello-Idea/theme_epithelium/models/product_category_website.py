from odoo import models,fields,api

class ProductCategory(models.Model):
    _name = "product.category.website"
    _description = "Product Category Epithelium"

    name = fields.Char()
    icon = fields.Binary()
    description = fields.Html()

