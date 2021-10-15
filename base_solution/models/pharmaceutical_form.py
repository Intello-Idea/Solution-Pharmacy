from odoo import models, fields, api

class PharmaceuticalForm(models.Model):
    _name = "pharmaceutical.form"
    _description = "Model that stores the dosage form"

    name = fields.Char(string="Compoung")
    code = fields.Integer()
    value = fields.Float(string='Value x gr')

    @api.model
    def default_get(self, fields):
        res = super(PharmaceuticalForm, self).default_get(fields)
        # Almacena el codigo por defecto al abrir la interfaz del modelo
        res.update({'code': len(self.env["pharmaceutical.form"].search([])) + 1})
        return res