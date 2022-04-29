from odoo import fields, models, api
import xmltodict
import pprint
import json
import xml.etree.ElementTree as ET


class ResConfigSettingsMod(models.TransientModel):
    _inherit = 'res.config.settings'

    def execute(self):
        super(ResConfigSettingsMod, self).execute()
        # self.enable_disable_wizard_reports(False)
        # self.enable_disable_account_menu(False)
        # Reiniciar pagina:
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def _method(self):
        # parameter = self.env['ir.config_parameter'].sudo()
        # self.enable_disable_wizard_reports(False)
        # self.enable_disable_account_menu(False)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

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
            menus_item = self.env["ir.ui.menu"].sudo().search([("parent_id.id", "=", menu.id)])
            for me_i in menus_item:
                if me_i.id != menu_except_auxiliary_acco.id and me_i.id != menu_except_journals_audit.id:
                    all_menus.append(me_i)
        return all_menus

    def action_client(self, action_window):
        pp = pprint.PrettyPrinter(indent=4)
        view = self.env["ir.ui.view"].browse(action_window.view_id.id)
        dictionS = json.dumps(xmltodict.parse(view.arch))
        diction = json.loads(dictionS)
        return diction["form"]["footer"]["button"][1]["@name"]

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
