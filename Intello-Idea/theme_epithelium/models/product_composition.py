from odoo import models, fields, api

class Composition(models.Model):
    _name = "composition"
    _description = "Composition Epithelium"

    product_id = fields.Many2one("product.template")
    composition = fields.Many2one("product.composition")

    name = fields.Char(related="composition.name")
    icon = fields.Binary(related="composition.icon")
    description = fields.Html(related="composition.description")

    @api.onchange("composition")
    def autocomplete(self):
        self.name = self.composition.name
        self.icon = self.composition.icon
        self.description = self.composition.description


class ProductComposition(models.Model):
    _name = "product.composition"
    _description = "Product Composition Epithelium"

    name = fields.Char()
    icon = fields.Binary()
    description = fields.Html()
