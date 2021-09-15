# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class ProductTemplate(models.Model):
    _inherit = "product.template"

    website = fields.Boolean(string="Website")
    use = fields.Text()
    tips = fields.Text()
    color = fields.Char(default='#009960')
    benefits = fields.Text()
    presentation = fields.Text()
    website_category = fields.Many2one("product.category.website")
    product_composition = fields.Many2many("composition", string="Composition")
    form_magistral = fields.Many2one("product.form.magistral")
    product_version = fields.One2many("product.version", "product_id")
    description = fields.Html()

    @api.onchange('product_composition')
    def contraint_composition(self):
        # Funcion que restringe mas de una misma composicion en los productos website
        for composition in self.product_composition:
            n_composition = 0
            for comp in self.product_composition:
                if composition.composition.id == comp.composition.id:
                    n_composition = n_composition + 1
            if n_composition > 1:
                raise exceptions.Warning("La composicion ya se encuentra")

    """def action_post(self):
        self.state = 'posted'
        return self.state

    def action_draft(self):
        self.state = 'draft'
        return self.state"""
