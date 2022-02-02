# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False):
        account_moves = super(SaleOrder, self)._create_invoices(grouped, final)

        for account_move in account_moves:
            for invoice_line in account_move.invoice_line_ids:
                if invoice_line.bonus:
                    sale_bonus_line = self.env['sale.order.line'].search([('id', '=', invoice_line.sale_line_ids.id)])
                    sale_line = self.env['sale.order.line'].search([('id', '=', sale_bonus_line.line_bonus_id.id)])
                    line_bonus_from = self.env['account.move.line'].search(
                        [('sale_line_ids.id', '=', sale_line.id)])
                    invoice_line.line_bonus_id = line_bonus_from.id

            account_move.with_context(check_move_validity=False)._recompute_dynamic_lines(True)

        return account_moves

    def bonification(self):
        delete_bonificate = self.env['sale.order.line'].search([('order_id', '=', self.id), ('bonus', '=', True)])
        delete_bonificate.unlink()

        unit_purchased = self.partner_id.zones_channels.detail.unit_purchased
        unit_bonus = self.partner_id.zones_channels.detail.unit_bonus

        order_lines = self.order_line
        activities_obj = self.env['partner.channel'].search(
            [('star_date', '<=', self.date_order.date()), ('final_date', '>=', self.date_order.date())])
        if activities_obj:
            for activity_obj in activities_obj:
                for line in order_lines:
                    if (
                            self.partner_id.id in activity_obj.client.ids or self.partner_id.zones_channels.id in activity_obj.partner_categorys_ids.ids) and line.product_id.id == activity_obj.product.id:
                        if activity_obj.bonificate_product and line.product_uom_qty >= activity_obj.unit_purchased:
                            invoice_bonus_line = self.env['sale.order.line'].create({
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'product_counterpart': line.product_counterpart.id,
                                'price_unit': 0,
                                'product_uom_qty': activities_obj.unit_bonus * (
                                        line.product_uom_qty // activity_obj.unit_purchased),
                                'order_id': self.id,
                                'bonus': True,
                                'line_bonus_id': line.id,
                            })
                            line_tax_ids = []
                            for tax_line in line.tax_id:
                                line_tax_ids.append(tax_line.id)

                            invoice_bonus_line.update({
                                'tax_id': line_tax_ids,
                            })
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.product_uom_qty // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['sale.order.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'product_uom_qty': unit_bonus * range_bonificate,
                                            'order_id': self.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_id:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_id': line_tax_ids,
                                        })
                        elif activity_obj.bonificate_gift and line.product_uom_qty >= activity_obj.unit_purchased:
                            invoice_bonus_line = self.env['sale.order.line'].create({
                                'product_id': activity_obj.product_bonificate_id.id,
                                'name': activity_obj.product_bonificate_id.name,
                                'product_counterpart': activity_obj.product_bonificate_id.product_counterpart.id,
                                'price_unit': 0,
                                'product_uom_qty': activities_obj.unit_bonus * (
                                        line.product_uom_qty // activity_obj.unit_purchased),
                                'order_id': self.id,
                                'bonus': True,
                                'line_bonus_id': line.id,
                            })
                            line_tax_ids = []
                            for tax_line in line.tax_id:
                                line_tax_ids.append(tax_line.id)

                            invoice_bonus_line.update({
                                'tax_id': line_tax_ids,
                            })
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.product_uom_qty // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['sale.order.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'product_uom_qty': unit_bonus * range_bonificate,
                                            'order_id': self.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_id:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_id': line_tax_ids,
                                        })
                        elif activity_obj.discount_percentage and line.product_uom_qty >= activity_obj.unit_purchased:
                            line.update({
                                'discount': activity_obj.percentage,
                                'subtotal_before_bonificate': line.price_subtotal
                            })
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.product_uom_qty // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['sale.order.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'product_uom_qty': unit_bonus * range_bonificate,
                                            'order_id': self.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_id:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_id': line_tax_ids,
                                        })
                        elif activity_obj.discount_value and line.product_uom_qty >= activity_obj.unit_purchased:
                            line.update({'price_subtotal': line.price_subtotal - \
                                                           (activity_obj.value * (
                                                                   line.product_uom_qty // activity_obj.unit_purchased)),
                                         'total_bonificate': activity_obj.value * (
                                                 line.product_uom_qty // activity_obj.unit_purchased),
                                         'subtotal_before_bonificate': line.price_subtotal})
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.product_uom_qty // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['sale.order.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'product_uom_qty': unit_bonus * range_bonificate,
                                            'order_id': self.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_id:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_id': line_tax_ids,
                                        })
                        else:
                            if unit_purchased > 0:
                                range_bonificate = (line.product_uom_qty // unit_purchased)
                                if range_bonificate > 0:
                                    invoice_bonus_line = self.env['sale.order.line'].create({
                                        'product_id': line.product_id.id,
                                        'name': line.name,
                                        'product_counterpart': line.product_counterpart.id,
                                        'price_unit': 0,
                                        'product_uom_qty': unit_bonus * range_bonificate,
                                        'order_id': self.id,
                                        'bonus': True,
                                        'line_bonus_id': line.id,
                                    })

                                    line_tax_ids = []
                                    for tax_line in line.tax_id:
                                        line_tax_ids.append(tax_line.id)

                                    invoice_bonus_line.update({
                                        'tax_id': line_tax_ids,
                                    })
                    else:
                        if unit_purchased > 0:
                            range_bonificate = (line.product_uom_qty // unit_purchased)
                            if range_bonificate > 0:
                                invoice_bonus_line = self.env['sale.order.line'].create({
                                    'product_id': line.product_id.id,
                                    'name': line.name,
                                    'product_counterpart': line.product_counterpart.id,
                                    'price_unit': 0,
                                    'product_uom_qty': unit_bonus * range_bonificate,
                                    'order_id': self.id,
                                    'bonus': True,
                                    'line_bonus_id': line.id,
                                })

                                line_tax_ids = []
                                for tax_line in line.tax_id:
                                    line_tax_ids.append(tax_line.id)

                                invoice_bonus_line.update({
                                    'tax_id': line_tax_ids,
                                })
        else:
            for line in order_lines:
                if unit_purchased > 0:
                    range_bonificate = (line.product_uom_qty // unit_purchased)
                    if range_bonificate > 0:
                        invoice_bonus_line = self.env['sale.order.line'].create({
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'product_counterpart': line.product_counterpart.id,
                            'price_unit': 0,
                            'product_uom_qty': unit_bonus * range_bonificate,
                            'order_id': self.id,
                            'bonus': True,
                            'line_bonus_id': line.id,
                        })

                        line_tax_ids = []
                        for tax_line in line.tax_id:
                            if tax_line.bonus_tax:
                                line_tax_ids.append(tax_line.bonus_tax.id)

                        invoice_bonus_line.update({
                            'tax_id': line_tax_ids,
                        })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bonus = fields.Boolean()
    line_bonus_id = fields.Many2one('sale.order.line')
    subtotal_before_bonificate = fields.Float('Subtotal before Bonificate')
    total_bonificate = fields.Float('Total Bonificate')

    def _prepare_invoice_line(self):
        invoice_line = super(SaleOrderLine, self)._prepare_invoice_line()

        invoice_line.update({
            'bonus': self.bonus,
        })
        return invoice_line

    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        super(SaleOrderLine, self)._compute_amount()

        for line in self:
            if line.bonus:
                sale_line = self.env['sale.order.line'].search([('id', '=', line.line_bonus_id.id)])
                price = sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id,
                                                partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_subtotal': 0,
                })
