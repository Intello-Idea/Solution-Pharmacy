# -*- coding: utf-8 -*-
from xml import etree

from odoo import fields, models, api, exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import date


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_type = fields.Many2one('ln10_co_intello.taxestype', ondelete='set null')
    base_tax = fields.Boolean('Tax apply base?')
    base_value = fields.Float('Base Value')

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False,
                    handle_price_include=True):
        """ Returns all information required to apply taxes (in self + their children in case of a tax group).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

            'handle_price_include' is used when we need to ignore all tax included in price. If False, it means the
            amount passed to this method will be considered as the base of all computations.

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'total_void'    : 0.0,    # Total with those taxes, that don't have an account set
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }],
        } """

        res = super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner, is_refund,
                                                  handle_price_include)

        if not is_refund:

            to_remove = []
            for tax in res['taxes']:

                tax_id = self.env['account.tax'].search([('name', '=', tax['name'])], limit=1)

                if tax_id.base_tax and tax_id.base_value > abs(res['total_excluded']):
                    res['total_included'] -= tax['amount']
                    to_remove.append(res['taxes'].index(tax))

            if to_remove:
                for remove in reversed(to_remove):
                    res['taxes'].pop(remove)

        return res


class AccountJournal(models.Model):
    _inherit = "account.journal"

    handle_book = fields.Boolean(string='Handle Book')
    selection_book = fields.One2many('selection.book', 'name')

    invoice_resolution = fields.Many2one('account.dian.resolution', 'Resolution Invoice')
    note_resolution = fields.Many2one('account.dian.resolution', 'Credit Note Resolution')

    @api.constrains('invoice_resolution', 'note_resolution')
    def constrain_invoice_resolution(self):
        """Metodo que permite verificar las resoluciones de la dian que no sean iguales"""

        for journal in self:
            if journal.invoice_resolution and journal.note_resolution:
                if journal.invoice_resolution == journal.note_resolution:
                    raise exceptions.ValidationError(_("Invoice resolution and resolution note cant equals"))


class AccountJournalBook(models.Model):
    _name = 'selection.book'
    _description = "Selection book for journal"

    name = fields.Char()
    book = fields.Many2one('accounting.book', string='Book')
    sequence = fields.Many2one('ir.sequence', string='Sequence')
    next_number = fields.Integer(string='Next Number')


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def book_principal(self):

        book_default = self._context.get('book_default', '')
        if book_default:
            return self.env['accounting.book'].browse(book_default)
        else:
            return self.env['accounting.book'].search([('book_principal', '=', True)])

    book = fields.Many2one('accounting.book', default=book_principal, string='Book')
    is_replicated = fields.Boolean(default=False)

    from_sale_order = fields.Boolean(default=False, copy=False)

    prefix = fields.Char('Prefix', copy=False)
    number = fields.Char('Number', copy=False)
    reverse_concept = fields.Many2one('ln10_co_intello.diancodes', string='Concept dian',
                                      domain=[('type', '=', 'creditnote')])
    resolution_id = fields.Many2one('account.dian.resolution')
    exchange_rate = fields.Float(string='Exchange rate')

    def generate_resolution_text(self):

        for account_move in self:

            text = ""

            if account_move.company_id.partner_id.fiscal_regime:
                text = account_move.company_id.partner_id.fiscal_regime.name

            for fiscal_responsibility in account_move.company_id.partner_id.fiscal_responsibility:
                text = text + " - " + fiscal_responsibility.name

            if account_move.company_id.partner_id.code_ciiu_primary.code:
                text = text + ". Actividad Económica " + account_move.company_id.partner_id.code_ciiu_primary.code

            cuenta = 1
            for ciiu_secondary in account_move.company_id.partner_id.code_ciiu_secondary:
                if cuenta == len(account_move.company_id.partner_id.code_ciiu_secondary):
                    text = text + " Y " + ciiu_secondary.code
                else:
                    text = text + ", " + ciiu_secondary.code
                cuenta += 1

            if account_move.resolution_id and account_move.type in ["out_invoice", 'out_refund']:
                if account_move.type == "out_invoice":
                    text = text + "\nAutorización de numeración de facturación"
                else:
                    text = text + "\nAutorización de numeración"

                if account_move.resolution_id.type == "electronic":
                    text = text + " electronica"

                text = text + "\nNo. " + str(account_move.resolution_id.resolution) + " del " + str(
                    account_move.resolution_id.date.strftime('%d/%m/%y')) + "\nHabilita del " + str(
                    account_move.resolution_id.ini_date.strftime('%d/%m/%y')) + " hasta " + str(
                    account_move.resolution_id.fin_date.strftime('%d/%m/%y'))

                if account_move.resolution_id.prefix:
                    text = text + " con prefijo " + \
                           account_move.resolution_id.prefix + " y numeración del " + str(
                        account_move.resolution_id.ini_number) + " al " + str(
                        account_move.resolution_id.fin_number)

                else:
                    text = text + " con numeración del " + str(
                        account_move.resolution_id.ini_number) + " al " + str(
                        account_move.resolution_id.fin_number)

            return text

    @api.model
    def update_resolution_id(self):
        invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('resolution_id', '=', False)])
        if invoices:
            for invoice in invoices:
                if invoice.journal_id.invoice_resolution:
                    invoice.update({
                        'resolution_id': invoice.journal_id.invoice_resolution,
                    })

        credit_notes = self.env['account.move'].search([('move_type', '=', 'out_refund'), ('resolution_id', '=', False)])
        if credit_notes:
            for credit_note in credit_notes:
                if credit_note.journal_id.note_resolution:
                    credit_note.update({
                        'resolution_id': credit_note.journal_id.note_resolution,
                    })

    @api.model
    def update_book_id(self):
        invoices = self.env['account.move'].search([('book', '=', False)])
        book = self.env['accounting.book'].search([('name', '=', 'NIIF')])
        if invoices:
            for invoice in invoices:
                if invoice:
                    invoice.update({
                        'book': book.id
                    })

    @api.onchange('line_ids')
    def verification_own_account(self):
        account_line = self.line_ids.account_id
        for account in account_line:
            own_accounts = self.env['own.accounts'].search(
                [('book.id', '!=', self.book.id), ('accounting_account.id', '=', account.id)])
            if own_accounts:
                raise exceptions.ValidationError('Esta cuenta es propia de el libro ' + own_accounts.book.name)
            else:
                for line in self.line_ids:
                    line.book = self.book.id
                    line.update({
                        'book': self.book.id
                    })

    @api.onchange('narration')
    def fix_narration_note(self):
        if self.narration:
            self.narration = self.narration.strip()

    def verification_invoice_resolution(self):
        """Metodo que verifica si el diario tiene una resolución de factura
        tanto para facturas como para nota credito"""

        if self.journal_id:
            if self.journal_id.type == 'sale':

                if self.type == 'out_invoice':
                    if not self.journal_id.invoice_resolution:
                        raise exceptions.Warning(_("The journal has not Invoice Resolution"))

                    if self.invoice_date:
                        if not ((self.invoice_date >= self.journal_id.invoice_resolution.ini_date) and (
                                self.invoice_date <= self.journal_id.invoice_resolution.fin_date)):
                            raise exceptions.Warning(
                                _("The Invoice date is not in the range of the Invoice Resolution"))

                    if not self.journal_id.sequence_id.prefix == self.journal_id.invoice_resolution.prefix:
                        raise exceptions.Warning(
                            _("The sequence prefix and the Invoice Resolution prefix have to match"))

                if self.type == 'out_refund':

                    if self.journal_id.note_resolution:
                        if self.invoice_date:
                            if not ((self.invoice_date >= self.journal_id.note_resolution.ini_date) and (
                                    self.invoice_date <= self.journal_id.note_resolution.fin_date)):
                                raise exceptions.Warning(
                                    _("The Invoice date is not in the range of the Invoice Resolution"))

                            if not self.journal_id.sequence_id.prefix == self.journal_id.note_resolution.prefix:
                                raise exceptions.Warning(
                                    _("The sequence prefix and the Invoice Resolution prefix have to match"))

    def amount_to_text(self):
        text = self.currency_id.amount_to_text(self.amount_total).upper()
        return text

    @api.model
    def check_multibook(self):
        parameter = self.env['ir.config_parameter'].sudo()
        multibook = parameter.get_param('res.config.settings.multi_book')
        return multibook

    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        moves = self.filtered(lambda move: move.state == 'posted')
        if not moves:
            return

        self.flush()

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
                SELECT move2.id
                FROM account_move move
                INNER JOIN account_move move2 ON
                    move2.name = move.name
                    AND move2.journal_id = move.journal_id
                    AND move2.type = move.type
                    AND move2.book = move.book
                    AND move2.id != move.id
                WHERE move.id IN %s AND move2.state = 'posted'
            ''', [tuple(moves.ids)])
        res = self._cr.fetchone()
        if res:
            raise ValidationError(_('Posted journal entry must have an unique sequence number per company.'))

    def replication_account_book(self):

        books = self.env['accounting.book'].search([('id', '!=', self.book.id)])
        for book in books:
            for move in self:
                self.ensure_one()
                new_move = self.copy_data()[0]
                new_move.update({
                    "ref": move.ref,
                    "name": move.name,
                    "book": book.id,
                    "prefix": move.prefix,
                    "number": move.number,
                    "type": "entry",
                    "is_replicated": True,
                    'invoice_line_ids': None,
                })
                # To avoid to create a translation in the lang of the user, copy_translation will do it
                move_book = self.with_context(lang=None).create(new_move)
                self.change_account(book, move_book)

                move_book.post()

                self.env["relation.account.move"].create({
                    'src_book': self.book.id,
                    'src_move_id': self.id,
                    # generate move
                    'dst_book': book.id,
                    'dst_move_id': move_book.id,
                })

    def _get_sequence(self):
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''
        sequence = super(AccountMove, self)._get_sequence()
        if self.journal_id.handle_book:
            sequence = self.env['selection.book'].search([('book', '=', self.book.id)]).sequence

        """interpolated_prefix, interpolated_suffix = sequence._get_prefix_suffix()
        self.write({
            'prefix': interpolated_prefix
        })"""

        return sequence

    @api.model
    def default_get(self, vals):
        res = super(AccountMove, self).default_get(vals)
        res['invoice_date'] = fields.Date.today()
        return res

    @api.model
    def create(self, vals):
        account_move = super(AccountMove, self).create(vals)
        if self.move_type == 'out_invoice':
            self._validate_quota_client(account_move.amount_residual, account_move.partner_id)

        return account_move

    def write(self, vals):

        for rec in self:

            if rec.move_type == 'out_invoice':
                vals['resolution_id'] = rec.journal_id.invoice_resolution
                if vals.get('state', False):
                    if vals['state'] == 'posted':
                        amount_residual = rec.amount_residual
                        partner_id = rec.partner_id
                        rec._validate_quota_client(amount_residual, partner_id)

            if rec.move_type == 'out_refund':
                if rec.journal_id.note_resolution:
                    vals['resolution_id'] = rec.journal_id.note_resolution

            if rec.move_type != 'entry':
                if 'name' in vals and vals.get('name') != '/':
                    if rec.prefix:
                        vals['number'] = vals['name'].split(rec.prefix, 1)[1]
                    else:
                        words = str(vals.get('name')).replace('[', '').replace(']', '')
                        number = [int(word) for word in words if word.isdigit()]
                        num = ''
                        for item in number:
                            num += str(item)
                        vals['number'] = num

                    rec._validate_resolution_data(next_number=int(vals['number']))

        return super(AccountMove, self).write(vals)

    def _validate_quota_client(self, amount_total, partner_id):
        if partner_id.quota_client != 0 and not self.from_sale_order:
            if amount_total > partner_id.quota_total_remaining:
                raise exceptions.Warning(_(
                    'The amount of the sales order completes the client quota'))

    def _validate_resolution_data(self, next_number):

        if self.journal_id.type == 'sale':

            if self.type == 'out_invoice':

                if not ((next_number >= self.journal_id.invoice_resolution.ini_number) and (
                        next_number <= self.journal_id.invoice_resolution.fin_number)):
                    raise exceptions.ValidationError(
                        _("The next sequence number is not in the invoice resolution range"))

                if self.invoice_date:
                    if not ((self.invoice_date >= self.journal_id.invoice_resolution.ini_date) and (
                            self.invoice_date <= self.journal_id.invoice_resolution.fin_date)):
                        raise exceptions.ValidationError(
                            _("The Invoice date is not in the range of the Invoice Resolution"))

                if not self.journal_id.sequence_id.prefix == self.journal_id.invoice_resolution.prefix:
                    raise exceptions.ValidationError(_(
                        "The sequence prefix and the Invoice Resolution prefix have to match"))

            if self.type == 'out_refund':

                if self.journal_id.note_resolution:
                    if not ((next_number >= self.journal_id.note_resolution.ini_number) and (
                            next_number <= self.journal_id.note_resolution.fin_number)):
                        raise exceptions.ValidationError(_(
                            "The next sequence number is not in the invoice resolution range"))

                    if self.invoice_date:
                        if not ((self.invoice_date >= self.journal_id.note_resolution.ini_date) and (
                                self.invoice_date <= self.journal_id.note_resolution.fin_date)):
                            raise exceptions.ValidationError(_(
                                "The Invoice date is not in the range of the Invoice Resolution"))

                        if not self.journal_id.refund_sequence_id.prefix == self.journal_id.note_resolution.prefix:
                            raise exceptions.ValidationError(_(
                                "The sequence prefix and the Invoice Resolution prefix have to match"))

    def change_account(self, book, new_move):

        year = int(new_move.date.strftime("%Y"))
        approved_accounts = book.detail.search([('year', '=', year)])
        if approved_accounts:
            for line in new_move.line_ids:
                for approved_account in approved_accounts:
                    if line.account_id == approved_account.count_account_base:
                        line.update({
                            "account_id": approved_account.count_approved_account
                        })

    def post(self):
        post = super(AccountMove, self).post()
        for record in self:
            if record.check_multibook() and not record.journal_id.handle_book and not record.is_replicated:
                record.replication_account_book()

        return post

    def month_block(self):

        today = date.today()
        date_month = (today.strftime("%m"))
        date_year = int(today.strftime("%Y"))
        month_block = self.book.month_block.search(
            [('book.id', '=', self.book.id), ('year', '=', date_year), ('month', '=', date_month)])

        if month_block:
            if month_block.is_closed:
                raise exceptions.ValidationError("El libro y el mes en que se hace la publicación ya esta cerrado")
        else:
            raise exceptions.ValidationError(
                "Bloqueo de mes no definido para el libro " + str(self.book.name) + ". En el año " + str(
                    date_year) + " y mes " + str(date_month))

            # -------- Herencia a acciones en botones ---

    def action_post(self):
        self.month_block()
        action_post = super(AccountMove, self).action_post()
        return action_post

    def button_draft(self):
        if self.is_replicated:
            raise exceptions.ValidationError("Operación no permitida, Movimiento generado desde otro libro")
        else:
            self.month_block()
            draft_move = super(AccountMove, self).button_draft()

        relation_account_move = self.env['relation.account.move'].search(
            [('src_move_id.id', '=', self.id), ('src_book.id', '=', self.book.id)])
        for relation_move in relation_account_move:
            account_move = self.env['account.move'].browse(relation_move.dst_move_id.id)
            account_move.update({
                'name': '/',
            })
            account_move.unlink()
            relation_move.unlink()

        return draft_move

    @api.onchange('currency_id', 'invoice_date')
    def _exchange_rate(self):
        """
        Metodo que calcula la tasa de cambio de la moneda segun los campos de moneda y fecha.
        @author Julián Valdés - Intello Idea
        """
        if self.currency_id.id != self.company_id.currency_id.id:
            rate = self.env['res.currency.rate'].search(
                [('currency_id.id', '=', self.currency_id.id), ('name', '=', self.invoice_date)])
            if rate:
                self.exchange_rate = rate.value
            else:
                raise exceptions.ValidationError("Please, modify the exchange rate for the selected date")
            print(self.exchange_rate)


class RelationAccountMove(models.Model):
    _name = "relation.account.move"
    _description = "relation of account move in books"

    src_book = fields.Many2one('accounting.book')
    src_move_id = fields.Many2one('account.move')

    # Generate move
    dst_book = fields.Many2one('accounting.book')
    dst_move_id = fields.Many2one('account.move')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    book = fields.Many2one('accounting.book', string="Book")
    team_id = fields.Many2one('crm.team', related='move_id.team_id', store=True)
    parent_category_id = fields.Many2one('product.category', compute='_compute_parent_category_id', store=True)

    @api.depends('team_id', 'product_id')
    def _compute_parent_category_id(self):
        for rec in self:
            if rec.team_id and rec.product_id.categ_id.parent_id:
                rec.parent_category_id = rec.product_id.categ_id.parent_id.id
            elif rec.team_id and rec.product_id.categ_id:
                rec.parent_category_id = rec.product_id.categ_id.id
            else:
                rec.parent_category_id = False

    def _amount_residual(self):
        super(AccountMoveLine, self)._amount_residual()

        for line in self:
            if line.move_id.is_replicated:
                line.reconciled = True

    # query
    @api.model
    def _query_get(self, domain=None):
        if domain:
            domain = domain
        else:
            domain = []
        parameter = self.env['ir.config_parameter'].sudo()
        multibook = parameter.get_param('res.config.settings.multi_book')
        if multibook:
            book_w = self.env['book.report.wizard'].search([])[-1]
            domain += [("move_id.book.id", "=", book_w.book_id.id)]

        else:
            book_w = self.env['accounting.book'].search([("book_principal", "=", True)])
            domain += [("move_id.book.id", "=", book_w.id)]

        return super(AccountMoveLine, self)._query_get(domain)

    def action_sale(self, name, book_id):

        if name == 'General Ledger':
            context = {'journal_type': 'general', 'search_default_group_by_account': 1, 'search_default_posted': 1}

        elif name == 'Partner Ledger':
            context = {'journal_type': 'general', 'search_default_group_by_partner': 1, 'search_default_posted': 1,
                       'search_default_payable': 1, 'search_default_receivable': 1, 'search_default_unreconciled': 1}
        elif name == 'Miscellaneous':
            context = {'journal_type': 'general', 'search_default_group_by_move': 1, 'search_default_posted': 1,
                       'search_default_misc_filter': 1, 'name_groupby': 1, 'expand': 1}

        elif name == 'Bank and Cash':
            context = {'journal_type': 'bank', 'search_default_group_by_move': 1, 'search_default_posted': 1,
                       'search_default_bank': 1, 'search_default_cash': 1, 'name_groupby': 1, 'expand': 1}
        elif name == 'Purchases':
            context = {'journal_type': 'purchase', 'search_default_group_by_move': 1, 'search_default_posted': 1,
                       'search_default_purchases': 1, 'name_groupby': 1, 'expand': 1}
        elif name == 'Sales':
            context = {'journal_type': 'sales', 'search_default_group_by_move': 1, 'search_default_posted': 1,
                       'search_default_sales': 1, 'name_groupby': 1, 'expand': 1}

        action = {
            "type": "ir.actions.act_window",
            'name': name,
            "view_mode": "tree,pivot,graph",
            "res_model": 'account.move.line',
            "context": context,

            "domain": [('display_type', 'not in', ('line_section', 'line_note')),
                       ('move_id.book', '=', book_id)],
        }
        return action


class AccountMonthBlock(models.Model):
    _name = "account.month.block"
    _order = "book, year desc, month desc"
    _description = "month block for account in account move"

    name = fields.Char(compute="compute_name", store=True)
    book = fields.Many2one('accounting.book', string='Book')
    year = fields.Integer(string='Year')
    month = fields.Selection(
        [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
         ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')])

    is_closed = fields.Boolean(string="Closed", default=False)

    _sql_constraints = [
        ('month_unique', 'UNIQUE(book,year,month)', "you can't have a repeated month and year for book!")]

    @api.depends('year', 'month')
    def compute_name(self):
        self.name = str(self.month) + "/" + str(self.year) + "/ " + "Bloqueado: " + str(self.is_closed)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    book_account_name = fields.One2many('book.account.name', 'account_id')


class BookAccountName(models.Model):
    _name = 'book.account.name'
    _description = 'detail account for book'

    account_id = fields.Many2one('account.account')
    book = fields.Many2one('accounting.book', string="Book")
    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('Unique_book', 'UNIQUE (account_id,book)', '!you can not have more than one name for a book¡'), ]


class account_payment(models.Model):
    _inherit = "account.payment"

    def button_journal_entries(self):
        views = [(self.env.ref('account.view_move_line_tree').id, 'tree'),
                 (self.env.ref('account.view_move_line_form').id, 'form')]
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.ids), ('move_id.book.name', '=', 'NIIF')],
        }
