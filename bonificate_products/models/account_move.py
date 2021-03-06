# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def bonification(self):
        delete_bonificate = self.env['account.move.line'].search([('move_id', '=', self.id), ('bonus', '=', True)])
        delete_bonificate.unlink()

        unit_purchased = self.partner_id.zones_channels.detail.unit_purchased
        unit_bonus = self.partner_id.zones_channels.detail.unit_bonus

        order_lines = self.invoice_line_ids
        activities_obj = self.env['partner.channel'].search(
            [('star_date', '<=', self.invoice_date), ('final_date', '>=', self.invoice_date)])
        if activities_obj:
            for activity_obj in activities_obj:
                for line in order_lines:
                    if (
                            self.partner_id.id in activity_obj.client.ids or self.partner_id.zones_channels.id in activity_obj.partner_categorys_ids.ids) and line.product_id.id == activity_obj.product.id:
                        if activity_obj.bonificate_product and line.quantity >= activity_obj.unit_purchased:
                            invoice_bonus_line = self.env['account.move.line'].create({
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'product_counterpart': line.product_counterpart.id,
                                'price_unit': 0,
                                'quantity': activities_obj.unit_bonus * (line.quantity // activity_obj.unit_purchased),
                                'move_id': self.id,
                                'account_id': line.account_id.id,
                                'bonus': True,
                                'line_bonus_id': line.id,
                            })
                            line_tax_ids = []
                            for tax_line in line.tax_ids:
                                line_tax_ids.append(tax_line.id)

                            invoice_bonus_line.update({
                                'tax_ids': line_tax_ids,
                            })
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.quantity // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['account.move.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'quantity': unit_bonus * range_bonificate,
                                            'move_id': self.id,
                                            'account_id': line.account_id.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_ids:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_ids': line_tax_ids,
                                        })
                        elif activity_obj.bonificate_gift and line.quantity >= activity_obj.unit_purchased:
                            invoice_bonus_line = self.env['account.move.line'].create({
                                'product_id': activity_obj.product_bonificate_id.id,
                                'name': activity_obj.product_bonificate_id.name,
                                'product_counterpart': activity_obj.product_bonificate_id.product_counterpart.id,
                                'price_unit': 0,
                                'quantity': activities_obj.unit_bonus * (line.quantity // activity_obj.unit_purchased),
                                'move_id': self.id,
                                'account_id': line.account_id.id,
                                'bonus': True,
                                'line_bonus_id': line.id,
                            })
                            line_tax_ids = []
                            for tax_line in line.tax_ids:
                                line_tax_ids.append(tax_line.id)

                            invoice_bonus_line.update({
                                'tax_ids': line_tax_ids,
                            })
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.quantity // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['account.move.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'quantity': unit_bonus * range_bonificate,
                                            'move_id': self.id,
                                            'account_id': line.account_id.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_ids:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_ids': line_tax_ids,
                                        })
                        elif activity_obj.discount_value and line.quantity >= activity_obj.unit_purchased:
                            line.update({'price_subtotal': line.price_subtotal - \
                                                           (activity_obj.value * (
                                                                   line.quantity // activity_obj.unit_purchased)),
                                         'total_bonificate': activity_obj.value * (
                                                 line.quantity // activity_obj.unit_purchased),
                                         'subtotal_before_bonificate': line.price_subtotal})
                            if activity_obj.bonificate_category:
                                if unit_purchased > 0:
                                    range_bonificate = (line.quantity // unit_purchased)
                                    if range_bonificate > 0:
                                        invoice_bonus_line = self.env['account.move.line'].create({
                                            'product_id': line.product_id.id,
                                            'name': line.name,
                                            'product_counterpart': line.product_counterpart.id,
                                            'price_unit': 0,
                                            'quantity': unit_bonus * range_bonificate,
                                            'move_id': self.id,
                                            'account_id': line.account_id.id,
                                            'bonus': True,
                                            'line_bonus_id': line.id,
                                        })

                                        line_tax_ids = []
                                        for tax_line in line.tax_ids:
                                            line_tax_ids.append(tax_line.id)

                                        invoice_bonus_line.update({
                                            'tax_ids': line_tax_ids,
                                        })
                        else:
                            if unit_purchased > 0:
                                range_bonificate = (line.quantity // unit_purchased)
                                if range_bonificate > 0:
                                    invoice_bonus_line = self.env['account.move.line'].create({
                                        'product_id': line.product_id.id,
                                        'name': line.name,
                                        'product_counterpart': line.product_counterpart.id,
                                        'price_unit': 0,
                                        'quantity': unit_bonus * range_bonificate,
                                        'move_id': self.id,
                                        'account_id': line.account_id.id,
                                        'bonus': True,
                                        'line_bonus_id': line.id,
                                    })

                                    line_tax_ids = []
                                    for tax_line in line.tax_ids:
                                        line_tax_ids.append(tax_line.id)

                                    invoice_bonus_line.update({
                                        'tax_ids': line_tax_ids,
                                    })
                    else:
                        if unit_purchased > 0:
                            range_bonificate = (line.quantity // unit_purchased)
                            if range_bonificate > 0:
                                invoice_bonus_line = self.env['account.move.line'].create({
                                    'product_id': line.product_id.id,
                                    'name': line.name,
                                    'product_counterpart': line.product_counterpart.id,
                                    'price_unit': 0,
                                    'quantity': unit_bonus * range_bonificate,
                                    'move_id': self.id,
                                    'account_id': line.account_id.id,
                                    'bonus': True,
                                    'line_bonus_id': line.id,
                                })

                                line_tax_ids = []
                                for tax_line in line.tax_ids:
                                    line_tax_ids.append(tax_line.id)

                                invoice_bonus_line.update({
                                    'tax_ids': line_tax_ids,
                                })
        else:
            for line in order_lines:
                if unit_purchased > 0:
                    range_bonificate = (line.quantity // unit_purchased)
                    if range_bonificate > 0:
                        invoice_bonus_line = self.env['account.move.line'].create({
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'product_counterpart': line.product_counterpart.id,
                            'price_unit': 0,
                            'quantity': unit_bonus * range_bonificate,
                            'move_id': self.id,
                            'account_id': line.account_id.id,
                            'bonus': True,
                            'line_bonus_id': line.id,
                        })

                        line_tax_ids = []
                        for tax_line in line.tax_ids:
                            if tax_line.bonus_tax:
                                line_tax_ids.append(tax_line.bonus_tax.id)

                        invoice_bonus_line.update({
                            'tax_ids': line_tax_ids,
                        })

        self.with_context(check_move_validity=False)._recompute_dynamic_lines(True)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        ''' Compute the dynamic tax lines of the journal entry.

        :param lines_map: The line_ids dispatched by type containing:
            * base_lines: The lines having a tax_ids set.
            * tax_lines: The lines having a tax_line_id set.
            * terms_lines: The lines generated by the payment terms of the invoice.
            * rounding_lines: The cash rounding lines of the invoice.
        '''
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice():
                if not base_line.bonus:
                    price_unit = base_line.price_unit
                    discount = base_line.discount
                    currency_id = base_line.currency_id
                else:
                    bonus_from_line = self.env['account.move.line'].search([('id', '=', base_line.line_bonus_id.ids)])

                    price_unit = bonus_from_line.price_unit
                    discount = bonus_from_line.discount
                    currency_id = bonus_from_line.currency_id

                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                if currency_id:
                    price_unit_foreign_curr = sign * price_unit * (1 - (discount / 100.0))
                    price_unit_comp_curr = currency_id._convert(price_unit_foreign_curr,
                                                                move.company_id.currency_id, move.company_id,
                                                                move.date)
                else:
                    price_unit_foreign_curr = 0.0
                    price_unit_comp_curr = sign * price_unit * (1 - (discount / 100.0))
            else:
                quantity = 1.0
                price_unit_foreign_curr = base_line.amount_currency
                price_unit_comp_curr = base_line.balance

            balance_taxes_res = base_line.tax_ids._origin.compute_all(
                price_unit_comp_curr,
                currency=base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=self.type in ('out_refund', 'in_refund'),
            )

            if base_line.currency_id:
                # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
                amount_currency_taxes_res = base_line.tax_ids._origin.compute_all(
                    price_unit_foreign_curr,
                    currency=base_line.currency_id,
                    quantity=quantity,
                    product=base_line.product_id,
                    partner=base_line.partner_id,
                    is_refund=self.type in ('out_refund', 'in_refund'),
                )
                for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
                    tax = self.env['account.tax'].browse(b_tax_res['id'])
                    b_tax_res['amount_currency'] = ac_tax_res['amount']

                    # A tax having a fixed amount must be converted into the company currency when dealing with a
                    # foreign currency.
                    if tax.amount_type == 'fixed':
                        b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'],
                                                                             move.company_id.currency_id,
                                                                             move.company_id, move.date)

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        self.line_ids -= to_remove

        # ==== Mount base lines ====
        # remove = self.line_ids
        for line in self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab):
            # Don't call compute_all if there is no tax.

            if not line.tax_ids:
                line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            line.tag_ids = compute_all_vals['base_tags']

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                    tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['balance'] += tax_vals['amount']
                taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
                taxes_map_entry['tax_base_amount'] += tax_vals['base']
                taxes_map_entry['grouping_dict'] = grouping_dict
            line.tax_exigible = tax_exigible

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # Don't create tax lines with zero balance.
            if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(
                    taxes_map_entry['amount_currency']):
                taxes_map_entry['grouping_dict'] = False

            tax_line = taxes_map_entry['tax_line']
            tax_base_amount = -taxes_map_entry['tax_base_amount'] if self.is_inbound() else taxes_map_entry[
                'tax_base_amount']

            if not tax_line and not taxes_map_entry['grouping_dict']:
                continue
            elif tax_line and not taxes_map_entry['grouping_dict']:
                # The tax line is no longer used, drop it.
                self.line_ids -= tax_line
            elif tax_line:
                tax_line.update({
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                })
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                tax_line = create_method({
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bonus = fields.Boolean()
    line_bonus_id = fields.Many2one('account.move.line')
