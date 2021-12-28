# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class RateBonification(models.Model):
    _name = "rate.bonification"
    _description = "this module containt the rates for discount product"
    _rec_name = "name"

    name = fields.Char(string='Name')
    code = fields.Integer()
    lines_price = fields.One2many('rate.bonification.line', 'lines', string="lines price")
    check_validation = fields.Boolean(string="Validation values", default=True)

    @api.model
    def default_get(self, fields):
        res = super(RateBonification, self).default_get(fields)
        # Almacena el codigo por defecto al abrir la interfaz del modelo
        res.update({'code': len(self.env["rate.bonification"].search([])) + 1})
        return res
    
    @api.constrains('lines_price')
    def _validation_values(self):
        for line in self.lines_price:
            if line.start >= line.final:
                raise ValidationError("!ERROR, el valor ingresado en los limites no es coherente¡")
    
    @api.constrains('check_validation')
    def _check_ok(self):
        if self.check_validation == False:
            raise ValidationError("!Por favor revisar los valores que se tiene alguna incoherencia¡")
    
    @api.onchange('lines_price')
    def _validation_range(self):
        datos = []
        i = -1
        for line in self.lines_price:
            items = ()
            items = items+(line.start, line.final)
            datos.append(items)
        
        for record in datos:
            i += 1
            values = datos
            values.pop(i)
            for vals in values:
                if record[0] in range(vals[0],vals[1]+1):
                    self.check_validation = False
                    raise ValidationError("!ERROR, el valor ingresado en los limites no es coherente¡")
                else:
                    self.check_validation = True
                if record[1] in range(vals[0],vals[1]+1):
                    self.check_validation = False
                    raise ValidationError("!ERROR, el valor ingresado en los limites no es coherente¡")
                else:
                    self.check_validation = True

class RateBonificationLine(models.Model):
    _name = "rate.bonification.line"
    _description = "this module containt the lines rates for discount product"

    start = fields.Integer(string="Start")
    final = fields.Integer(string="Final")
    base_price = fields.Float(string="Base")
    lines = fields.Many2one('rate.bonification', string="Base Price")