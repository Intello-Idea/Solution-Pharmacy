from odoo import api, fields, models, exceptions


class BookAccountWizard(models.TransientModel):
    _name = "book.account.wizard"
    _description = "report for books"

    @api.model
    def book_principal(self):
        principal_book = self.env['accounting.book'].search([('book_principal', '=', True)])
        if not principal_book:
            raise exceptions.UserError("No existe un Libro principal.")
        else:
            return principal_book

    book_id = fields.Many2one("accounting.book", string="Book", default=book_principal, store=True)

    def render_report_sale(self):
        action = self.env['account.move.line'].action_sale('Sales', self.book_id.id)
        return action

    def render_report_purchase(self):
        action = self.env['account.move.line'].action_sale('Purchases', self.book_id.id)
        return action

    def render_report_bank(self):
        action = self.env['account.move.line'].action_sale('Bank and Cash', self.book_id.id)
        return action

    def render_report_misc(self):
        action = self.env['account.move.line'].action_sale('Miscellaneous', self.book_id.id)
        return action

    def render_report_general(self):
        action = self.env['account.move.line'].action_sale('General Ledger', self.book_id.id)
        return action

    def render_report_partner(self):
        action = self.env['account.move.line'].action_sale('Partner Ledger', self.book_id.id)
        return action
