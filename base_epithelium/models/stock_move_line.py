from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

#    due_date = fields.Datetime('Due Date', related="lot_id.life_date")
    due_date = fields.Datetime('Due Date')
    product_uom_qty = fields.Float(
        'Reserved', default=0.0, digits='Precision Mrp Five', required=True, copy=False)
    qty_done = fields.Float('Done', default=0.0, digits='Precision Mrp Five', copy=False)
