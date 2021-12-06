from odoo import fields, models, api
import xmltodict
import pprint
import json
import xml.etree.ElementTree as ET


class ResConfigSettingsMod(models.TransientModel):
    _inherit = 'res.config.settings'

    multi_book = fields.Boolean(string="Multi Book", default=False)

    def set_values(self):
        super(ResConfigSettingsMod, self).set_values()
        parameter = self.env['ir.config_parameter'].sudo()
        parameter.set_param('res.config.settings.multi_book', self.multi_book)

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsMod, self).get_values()
        parameter = self.env['ir.config_parameter'].sudo()
        multibook = parameter.get_param('res.config.settings.multi_book')
        res.update({'multi_book': multibook})
        return res

    def execute(self):
        super(ResConfigSettingsMod, self).execute()
        if self.multi_book:

            self.enable_disable_features_book(True)
#Carlos            self.enable_disable_wizard_reports(True)
            self.disable_enable_account_account(True)
#Carlos            self.enable_disable_account_menu(True)
#Carlos            self.enable_disable_account_menu(True)
        else:
            self.enable_disable_features_book(False)
            self.enable_disable_wizard_reports(False)
            self.disable_enable_account_account(False)
            self.enable_disable_account_menu(False)

        # Reiniciar pagina:
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def _method(self):
        parameter = self.env['ir.config_parameter'].sudo()
        multibook = parameter.get_param('res.config.settings.multi_book')
        if multibook:
            self.enable_disable_features_book(True)
#Carlos            self.enable_disable_wizard_reports(True)
            self.disable_enable_account_account(True)
#Carlos            self.enable_disable_account_menu(True)
        else:
            self.enable_disable_features_book(False)
            self.enable_disable_wizard_reports(False)
            self.disable_enable_account_account(False)
            self.enable_disable_account_menu(False)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def enable_disable_features_book(self, state):

        if state:

            # Multi book enable
            self.enable_disable_book_menus(True)

            action_account_multibook = self.env.ref("ln10_co_intello.action_accounting_book")
            action_multibook_accounting = self.env.ref("ln10_co_intello.action_multi_book_accounting")
            action_own_accounts = self.env.ref("ln10_co_intello.action_Own_Accounts")

            menu_account_multibook = self.env.ref("ln10_co_intello.menu_account_multibook")
            menu_multibook_accounting = self.env.ref("ln10_co_intello.menu_multi_book_accounting")
            menu_own_accounts = self.env.ref("ln10_co_intello.menu_action_Own_accounts")

            menu_account_multibook.update({
                "action": action_account_multibook
            })
            menu_multibook_accounting.update({
                "action": action_multibook_accounting
            })
            menu_own_accounts.update({
                "action": action_own_accounts
            })

            # Disable Journal
            journal_item = self.env.ref("account.menu_action_account_moves_all")
            journal_item.action = False

            journal_entries = self.env.ref("account.menu_action_move_journal_line_form")
            journal_entries.action = False

        else:
            # Multi book disable
            self.enable_disable_book_menus(False)

            menu_account_multibook = self.env.ref("ln10_co_intello.menu_account_multibook")
            menu_account_multibook.action = False

            menu_multibook_accounting = self.env.ref("ln10_co_intello.menu_multi_book_accounting")
            menu_multibook_accounting.action = False

            menu_own_accounts = self.env.ref("ln10_co_intello.menu_action_Own_accounts")
            menu_own_accounts.action = False

            # Enable journal
            action_journal_item = self.env.ref("account.action_account_moves_all")
            action_journal_entries = self.env.ref("account.action_move_journal_line")

            menu_journal_item = self.env.ref("account.menu_action_account_moves_all")
            menu_journal_entries = self.env.ref("account.menu_action_move_journal_line_form")

            menu_journal_item.update({
                "action": action_journal_item
            })

            menu_journal_entries.update({
                "action": action_journal_entries
            })

    def enable_disable_book_menus(self, state):

        account_book_menus = self.env["account.book.menu"].search([])

        for book_menu_action in account_book_menus:
            menu_item = self.env['ir.ui.menu'].browse(book_menu_action.menu_item_id.id)
            action = self.env['ir.actions.act_window'].browse(book_menu_action.action_id.id)
            if menu_item and action:
                if state:
                    menu_item.update({
                        "action": action
                    })
                else:
                    menu_item.action = False
            else:
                pass

    def enable_disable_wizard_reports(self, state):

        menus_reports = self.all_reports()
        if state:
            for menu_report in menus_reports:
                save = self.env["account.financial.report.save"]

                if not save.search([("menu_id.id", "=", menu_report.id)]):
                    # 'action_client': menu_report.action.id

                    view_new = self.env["ir.ui.view"].create({
                        'name': menu_report.name,
                        'model': "book.report.wizard",
                        'arch': self.action_render_view(menu_report.action.id, menu_report.name)
                    })

                    if self.report_is_multibook(menu_report.id):
                        vals = {
                            'name': menu_report.name,
                            'res_model': "book.report.wizard",
                            'type': "ir.actions.act_window",
                            'view_mode': "form",
                            'target': "new",
                            'view_id': view_new.id
                        }
                        new_action_window = self.env['ir.actions.act_window'].create(vals)
                        # 'action_client': menu_report.action.id,
                        save.create({
                            'menu_id': menu_report.id,
                            'action_window': new_action_window.id
                        })
                        menu_report.update({
                            "action": new_action_window
                        })
                    else:
                        continue


                else:
                    res = save.search([("menu_id.id", "=", menu_report.id)])
                    if self.report_is_multibook(menu_report.id):
                        res.action_window.update({
                            'name': menu_report.name,
                        })
                        menu_report.update({
                            "action": res.action_window
                        })
                    else:
                        continue

        else:
            for menu_report in menus_reports:
                save = self.env["account.financial.report.save"]
                if save.search([("menu_id.id", "=", menu_report.id)]):
                    """res = save.search([("menu_id.id", "=", menu_report.id)])
                    menu_report.update({
                        "action": res.action_client
                    })"""
                    res = save.search([("menu_id.id", "=", menu_report.id)])
                    action_client = self.env["ir.actions.client"].search(
                        [("id", "=", self.action_client(res.action_window))])
                    menu_report.update({
                        "action": action_client
                    })

    def enable_disable_account_menu(self, state):
        account_menus = self.account_menu()
        if state:
            for menu in account_menus:
                menu_item = self.env['account.book.menu.save'].search([('menu_id', '=', menu.id)])

                if not menu_item:
                    menu_save = self.env['account.book.menu.save'].create({
                        'menu_id': menu.id,
                        'action_window_old': menu.action.id,
                    })

                    ir_ui_view = {'name': menu.name, 'model': "book.account.wizard"}
                    if menu.name == 'Sale' or menu.name == 'Ventas':
                        ir_ui_view.update({'arch': self.action_render_account('sale', menu.name)})

                    elif menu.name == 'Purchases' or menu.name == 'Compras':
                        ir_ui_view.update({'arch': self.action_render_account('purchase', menu.name)})

                    elif menu.name == 'Bank and Cash' or menu.name == 'Banco y caja':
                        ir_ui_view.update({'arch': self.action_render_account('bank', menu.name)})

                    elif menu.name == 'Miscellaneous' or menu.name == 'Varios':
                        ir_ui_view.update({'arch': self.action_render_account('misc', menu.name)})

                    elif menu.name == 'General Ledger' or menu.name == 'Libro mayor':
                        ir_ui_view.update({'arch': self.action_render_account('general', menu.name)})

                    elif menu.name == 'Partner Ledger' or menu.name == 'Libro mayor de empresa':
                        ir_ui_view.update({'arch': self.action_render_account('partner', menu.name)})

                    view_new = self.env["ir.ui.view"].create(ir_ui_view)

                    vals = {
                        'name': menu.name,
                        'res_model': "book.account.wizard",
                        'type': "ir.actions.act_window",
                        'view_mode': "form",
                        'target': "new",
                        'view_id': view_new.id
                    }
                    new_action_window = self.env['ir.actions.act_window'].create(vals)
                    menu.write({
                        "action": new_action_window
                    })
                    menu_save.write({'action_window': new_action_window, })
                else:
                    menu.write({
                        'action': menu_item.action_window
                    })

        else:
            menu_item = self.env['account.book.menu.save'].search([])
            for menu in menu_item:
                menu.menu_id.write({
                    'action': menu.action_window_old,
                })

    def account_menu(self):
        account_menus = []
        account_menus.append(self.env.ref('account.menu_action_account_moves_journal_sales'))
        account_menus.append(self.env.ref('account.menu_action_account_moves_journal_purchase'))
        account_menus.append(self.env.ref('account.menu_action_account_moves_journal_bank_cash'))
        account_menus.append(self.env.ref('account.menu_action_account_moves_journal_misc'))
        account_menus.append(self.env.ref('account.menu_action_account_moves_ledger_general'))
        account_menus.append(self.env.ref('account.menu_action_account_moves_ledger_partner'))

        return account_menus

    def action_render_view(self, action_client, name):
        pp = pprint.PrettyPrinter(indent=4)

        view = self.env.ref("ln10_co_intello.book_report_wizard_view")

        dictionS = json.dumps(xmltodict.parse(view.arch))
        diction = json.loads(dictionS)
        diction["form"]["@string"] = name
        diction["form"]["footer"]["button"][1]["@name"] = action_client
        xml = xmltodict.unparse(diction)
        tree = ET.fromstring(xml)
        view.arch = ET.tostring(tree, encoding="unicode")

        return view.arch

    def action_render_account(self, action_client, name):
        pp = pprint.PrettyPrinter(indent=4)

        view = self.env.ref("ln10_co_intello.book_account_wizard_view")

        dictionS = json.dumps(xmltodict.parse(view.arch))
        diction = json.loads(dictionS)
        diction["form"]["@string"] = name
        diction["form"]["footer"]["button"][1]["@name"] = f"render_report_{action_client}"
        xml = xmltodict.unparse(diction)
        tree = ET.fromstring(xml)
        view.arch = ET.tostring(tree, encoding="unicode")

        return view.arch

    def all_reports(self):
        parent = self.env.ref("account.menu_finance_reports")
        menus_reports = self.env["ir.ui.menu"].sudo().search([("parent_id.id", "=", parent.id)])

        menu_except = []
        menu_except_auxiliary_acco = self.env.ref(
            "auxiliary_account_report.menu_action_account_report_auxiliary_report_wizard")
        menu_except_journals_audit = self.env.ref("account_reports.menu_print_journal")
        menu_aged_receivable = self.env.ref("account_reports.menu_action_account_report_aged_receivable")
        menu_aged_payable = self.env.ref("account_reports.menu_action_account_report_aged_payable")
        menu_except.append(menu_except_auxiliary_acco)
        menu_except.append(menu_except_journals_audit)
        menu_except.append(menu_aged_receivable)

        all_menus = []
        all_menus.append(menu_aged_receivable)
        all_menus.append(menu_aged_payable)
        for menu in menus_reports:
            # print(menu.name)
            menus_item = self.env["ir.ui.menu"].sudo().search([("parent_id.id", "=", menu.id)])
            # print("Menus Hijos")
            for me_i in menus_item:
                # print(me_i.name)
                if me_i.id != menu_except_auxiliary_acco.id and me_i.id != menu_except_journals_audit.id:
                    all_menus.append(me_i)
        return all_menus

    def action_client(self, action_window):
        pp = pprint.PrettyPrinter(indent=4)
        view = self.env["ir.ui.view"].browse(action_window.view_id.id)
        # view = self.env["ir.ui.view"].search([("id","=",action_window.view_id.id)])
        # action_client = self.env.ref("account_reports.action_account_report_pnl")
        # Print structure of dictionary
        # diction = pp.pprint(json.dumps(xmltodict.parse(view.arch)))
        # print(diction)

        # Dictionary string json
        dictionS = json.dumps(xmltodict.parse(view.arch))
        # Dictionary string to dictionary
        diction = json.loads(dictionS)
        # print(diction["form"]["footer"]["button"][1]["@name"])
        # mod dictionary
        return diction["form"]["footer"]["button"][1]["@name"]

    def report_is_multibook(self, menu_id):
        report_mul_book = []
        report_mul_book.append(self.env["account.financial.html.report"].sudo().search([]).generated_menu_id)

        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_partner_ledger"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_general_ledger"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_aged_receivable"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_aged_payable"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_coa"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_cj"))
        report_mul_book.append(self.env.ref("l10n_co_reports.menu_action_account_report_ica"))
        report_mul_book.append(self.env.ref("l10n_co_reports.menu_action_account_report_iva"))
        report_mul_book.append(self.env.ref("l10n_co_reports.menu_action_account_report_fuente"))
        report_mul_book.append(self.env.ref("ln10_co_intello.menu_action_quarterly_sales_report_all"))
        report_mul_book.append(self.env.ref("ln10_co_intello.menu_action_result_sales_report_sales"))
        report_mul_book.append(self.env.ref("ln10_co_intello.menu_action_result_sales_report_sales"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_account_report_cash_flow"))
        report_mul_book.append(self.env.ref("account.menu_configure_tax_report"))
        report_mul_book.append(self.env.ref("account_reports.menu_action_report_account_analytic"))
        report_mul_book.append(self.env.ref("account.action_account_invoice_report_all"))

        for repo in report_mul_book:
            if (len(repo) > 1):
                for r in repo:
                    if r.id == menu_id:
                        return True
            else:
                if repo.id == menu_id:
                    return True
        return False

    def disable_enable_account_account(self, state):
        if state:
            pp = pprint.PrettyPrinter(indent=4)

            view = self.env.ref("ln10_co_intello.view_inherit_account_account_form")

            # Print structure of dictionary
            #diction = pp.pprint(json.dumps(xmltodict.parse(view.arch)))
            #print(diction)

            # Dictionary string json
            dictionS = json.dumps(xmltodict.parse(view.arch))
            # Dictionary string to dictionary
            diction = json.loads(dictionS)
            #print(diction)
            # mod dictionary
            diction["xpath"]["notebook"]['page']["@invisible"] = "0"
            # Dictionary to xml
            # xml = dicttoxml.dicttoxml(diction).decode("utf-8")
            xml = xmltodict.unparse(diction)

            tree = ET.fromstring(xml)
            view.arch = ET.tostring(tree, encoding="unicode")

        else:
            pp = pprint.PrettyPrinter(indent=4)

            view = self.env.ref("ln10_co_intello.view_inherit_account_account_form")

            # Print structure of dictionary
            #diction = pp.pprint(json.dumps(xmltodict.parse(view.arch)))
            #print(diction)

            # Dictionary string json
            dictionS = json.dumps(xmltodict.parse(view.arch))
            # Dictionary string to dictionary
            diction = json.loads(dictionS)
            #print(diction)
            # mod dictionary
            diction["xpath"]["notebook"]['page']["@invisible"] = "1"
            # Dictionary to xml
            # xml = dicttoxml.dicttoxml(diction).decode("utf-8")
            xml = xmltodict.unparse(diction)

            tree = ET.fromstring(xml)
            view.arch = ET.tostring(tree, encoding="unicode")
