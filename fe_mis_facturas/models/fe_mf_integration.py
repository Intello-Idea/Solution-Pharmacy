# -*- coding: utf-8 -*-
from odoo import models, api, _, fields, exceptions
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta, date, datetime
import requests, time, base64, json
from http.client import responses as res


class FeMfConfiguration(models.Model):
    _name = "fe.mf.config"
    _description = "Fe with Mis Facturas"

    name = fields.Char(compute="compute_name", store=True)
    user = fields.Char('User')
    password = fields.Char('Password')
    url_web_service = fields.Char('Route')
    test = fields.Boolean('Test')
    test_mode = fields.Boolean('Test Mode')
    test_user = fields.Char('User')
    test_password = fields.Char('Password')
    test_url_web_service = fields.Char('Route')

    @api.constrains
    def one_configuration(self):
        if self.env['fe.mf.config'].search([('id', '!=', self.id)]):
            raise exceptions.ValidationError("Solo pude tener una configuración")

    @api.depends('user')
    def compute_name(self):
        self.name = self.user

    @api.model
    def create(self, vals_list):
        vals_list['test'] = self.env['fe.mf.methods'].login(vals_list['user'], vals_list['password'],
                                                            vals_list['url_web_service'])
        return super(FeMfConfiguration, self).create(vals_list)

    def write(self, vals_list):
        user = vals_list['user'] if 'user' in vals_list else self.user
        password = vals_list['password'] if 'password' in vals_list else self.password
        url = vals_list['url_web_service'] if 'url_web_service' in vals_list else self.url_web_service
        vals_list['test'] = self.env['fe.mf.methods'].login(user, password, url)
        return super(FeMfConfiguration, self).write(vals_list)

    @api.onchange('user', 'password', 'url_web_service')
    def disable_test(self):
        self.test = False


class FeMfLoginToken(models.TransientModel):
    _name = "fe.mf.login.token"
    _description = "Get token"

    date = fields.Date('Date')
    token = fields.Char('Token')
    # To-Do Agregar constrains de fecha


class FeMfMethods(models.AbstractModel):
    _name = "fe.mf.methods"
    _description = "Metodos para la interfaz del cliente API"

    def login(self, user="", password="", url=""):
        """
        Función para iniciar sesión en el servicio de Mis Facturas
        @param user: Usuario con el cual debe iniciar sesión
        @param password: Contraseña con la cual debe iniciar sesión
        @param url: Base de la url (cambia si es produccion o si es pruebas) donde debe enviar la paeticion de inicio de sesión
        @return: Booleano que representa eel estado del inicio de sesión
        """
        if user is " ":
            data = self.env['fe.mf.config'].search([])
            if not data:
                raise exceptions.ValidationError("Configure los datos de conexion al servicio de Mis Facturas")
            user = data.user
            password = data.password
            url = data.url
        today = date.today()
        url_service = str(url + "login/?username=" + user + "&password=" + password)
        payload = {}
        files = {}
        headers = {}
        response = requests.request("POST", url_service, headers=headers, data=payload, files=files)
        if response.status_code is 200:
            login = self.env['fe.mf.login.token'].search([('date', '=', today)])
            if not login:
                self.env['fe.mf.login.token'].create({
                    'date': today,
                    'token': str("misfacturas " + response.content.decode('utf8').split('"')[1])
                })
            return True
        else:
            raise exceptions.ValidationError("Error al conectar, usuario o contraseña incorrecta.")
            return False

    def _get_token(self, config):
        """
        Función para obtener el token de día, si no existe crea uno nuevo.
        @author Julian Valdes - Intello Idea
        @param config: Usuario, Contraseña, Url del servicio (sengun prueba o producción)
        @return:
        """
        today = date.today()
        env_token = self.env['fe.mf.login.token'].search([('date', '=', today)])
        if env_token:
            return env_token.token
        else:
            user = config.user
            password = config.password
            url_web_service = config.url_web_service
            if config.test_mode:
                user = config.test_user
                password = config.test_password
                url_web_service = config.test_url_web_service

            self.login(user, password, url_web_service)
            return self._get_token(config)

    def _get_parameters_connection(self):
        """
        Función para obtener token de acceso y url
        @author Julian Valdes - Intello Idea
        @return: Diccionario con el token de acceso y la url base del servicio
        """
        config = self.env['fe.mf.config'].search([])
        url_web_service = config.url_web_service
        if config.test_mode:
            url_web_service = config.test_url_web_service
        return {'token': self._get_token(config), 'url': url_web_service}

    def _get_parameters_settings(self):
        """
        Función para obtener parametros del res.config.settings
        @author Julian Valdes - Intello Idea
        @return: Diccionario con el token de acceso y la url base del servicio
        """
        parameter = self.env['ir.config_parameter'].sudo()
        fe_own_gr = parameter.get_param('res.config.settings.fe_own_gr')
        if fe_own_gr:
            fe_own_gr = "true"
        else:
            fe_own_gr = "false"
        return {'fe_own_gr': fe_own_gr}

    def load_invoice_line_data_to_json(self, template_id, posted_document):
        """
        Función que permite construir una lista de diccionaros con las lineas
        (productos e impuestos respectivos) de una factura o nota credito
        @author Julian Valdes - Intello Idea
        @param template_id: Plantilla según cual se construye el cuerpo de del json
        @param posted_document: Factura
        @return: Lista de diccionaros con las lineas
        """
        lines = []
        if template_id == 73:
            for line in posted_document.invoice_line_ids:
                if not line.display_type:
                    taxes = []
                    move_tax_line = self.env['account.move.taxes.line'].search(
                        [('move_line_id', '=', line.id), ('move_id', '=', line.move_id.id)])
                    line_total_taxes = 0
                    for tax in move_tax_line:
                        if not tax.tax_type_id.type == '07':
                            tax_information = {
                                "Id": tax.tax_type_id.type,
                                "TaxEvidenceIndicator": "false" if tax.tax_type_id.operation == "S" else "true",
                                "TaxableAmount": tax.base,
                                "TaxAmount": abs(tax.amount),
                                "Percent": abs(tax.percent),
                                "BaseUnitMeasure": 0,
                                "PerUnitAmount": 0
                            }
                            if tax_information['TaxEvidenceIndicator']:
                                line_total_taxes += tax.amount
                            taxes.append(tax_information)
                    price_product = 0
                    if line.sale_line_ids.bonus:
                        for product in posted_document.invoice_line_ids:
                            if line.product_id.name == product.product_id.name and \
                                    not product.sale_line_ids.bonus:
                                price_product = product.price_unit
                                break
                    else:
                        price_product = line.price_unit
                    product = {
                        "ItemReference": line.product_id.default_code,
                        "Name": line.product_id.name,
                        "Quatity": line.quantity,
                        "Price": price_product,
                        "LineAllowanceTotal": 0,
                        "LineChargeTotal": 0.0,
                        "LineTotalTaxes": line_total_taxes,
                        "LineTotal": (line.price_subtotal - line.discount) + line_total_taxes,
                        "LineExtensionAmount": line.price_subtotal,
                        "MeasureUnitCode": line.product_id.uom_id.dian_code.key_dian,
                        "FreeOFChargeIndicator": line.sale_line_ids.bonus,
                        "AdditionalReference": [],
                        "Note": "",
                        "AdditionalProperty": [],
                        "TaxesInformation": taxes,
                        "AllowanceCharge": [
                            {
                                "Id": 9,
                                "ChargeIndicator": False,
                                "AllowanceChargeReasonCode": 9,
                                "AllowanceChargeReason": "Descuento general",
                                "MultiplierFactorNumeric": line.discount,
                                "Amount": ((line.quantity * line.price_unit) * line.discount) / 100,
                                "BaseAmount": (line.quantity * line.price_unit)
                            }
                        ]
                    }
                    lines.append(product)

        if template_id == 91:
            for line in posted_document.invoice_line_ids:
                if not line.display_type:
                    taxes = []
                    move_tax_line = self.env['account.move.taxes.line'].search(
                        [('move_line_id', '=', line.id), ('move_id', '=', line.move_id.id)])
                    line_total_taxes = 0
                    for tax in move_tax_line:
                        if not tax.tax_type_id.type == '07':
                            tax_information = {
                                "Id": tax.tax_type_id.type,
                                "TaxEvidenceIndicator": "false" if tax.tax_type_id.operation == "S" else "true",
                                "TaxableAmount": tax.base,
                                "TaxAmount": abs(tax.amount),
                                "Percent": abs(tax.percent),
                                "BaseUnitMeasure": 0,
                                "PerUnitAmount": 0
                            }
                            if tax_information['TaxEvidenceIndicator']:
                                line_total_taxes += tax.amount
                            taxes.append(tax_information)
                    price_product = 0
                    if line.sale_line_ids.bonus:
                        for product in posted_document.invoice_line_ids:
                            if line.product_id.name == product.product_id.name and \
                                    not product.sale_line_ids.bonus:
                                price_product = product.price_unit
                                break
                    else:
                        price_product = line.price_unit
                    product = {
                        "ItemReference": line.product_id.default_code,
                        "Name": line.product_id.name,
                        "Quatity": line.quantity,
                        "Price": price_product,
                        "LineAllowanceTotal": 0,
                        "LineChargeTotal": 0.0,
                        "LineTotalTaxes": line_total_taxes,
                        "LineTotal": (line.price_subtotal - line.discount) + line_total_taxes,
                        "LineExtensionAmount": line.price_subtotal,
                        "MeasureUnitCode": line.product_id.uom_id.dian_code.key_dian,
                        "FreeOFChargeIndicator": line.sale_line_ids.bonus,
                        "AdditionalReference": [],
                        "Note": "",
                        "AdditionalProperty": [],
                        "TaxesInformation": taxes,
                        "AllowanceCharge": [
                            {
                                "Id": 9,
                                "ChargeIndicator": False,
                                "AllowanceChargeReasonCode": 9,
                                "AllowanceChargeReason": "Descuento general",
                                "MultiplierFactorNumeric": line.discount,
                                "Amount": ((line.quantity * line.price_unit) * line.discount) / 100,
                                "BaseAmount": (line.quantity * line.price_unit)
                            }
                        ]
                    }
                    lines.append(product)

        return lines

    def load_invoice_total_tax_to_json(self, template_id, posted_document):
        """
        Función que permite construir una lista de diccionaros con los totales de
        impuestos de la factura o nota credito
        @author Julian Valdes - Intello Idea
        @param template_id: Plantilla según cual se construye el cuerpo de del json
        @param posted_document: Factura
        @return: Lista de diccionaros con los totales de impuestos
        """
        lines = []
        if template_id == 73:
            move_tax = self.env['account.move.taxes'].search([('move_id', '=', posted_document.id)])
            for tax in move_tax:
                lines.append({
                    "Id": tax.tax_type_id.type,
                    "TaxEvidenceIndicator": "false" if tax.tax_type_id.operation == "S" else "true",
                    "TaxableAmount": tax.base,
                    "TaxAmount": abs(tax.amount),
                    "Percent": abs(tax.percent),
                    "BaseUnitMeasure": 0,
                    "PerUnitAmount": 0
                })

        if template_id == 91:
            move_tax = self.env['account.move.taxes'].search([('move_id', '=', posted_document.id)])
            for tax in move_tax:
                lines.append({
                    "Id": tax.tax_type_id.type,
                    "TaxEvidenceIndicator": "false" if tax.tax_type_id.operation == "S" else "true",
                    "TaxableAmount": tax.base,
                    "TaxAmount": abs(tax.amount),
                    "Percent": abs(tax.percent),
                    "BaseUnitMeasure": 0,
                    "PerUnitAmount": 0
                })
        return lines

    def load_ed_data_to_json(self, template_id, posted_document, gr, documents):
        """
        Función que permite construir un diccionario a partir de una factura o nota credito para luego
        ser enviada como json al servicio de Mis Facturas
        @author Julian Valdes - Intello Idea
        @param gr: Reprentación grafica
        @param template_id: Plantilla según cual se construye el cuerpo de del json
        @param posted_document: Factura
        @return: Diccionario con los valores de una factura
        """
        data_json = {}
        if template_id == 73:
            tax_total = self.load_invoice_total_tax_to_json(template_id, posted_document)
            tax_exclusive_amount = 0
            tax_inclusive_amount = 0
            for tax in tax_total:
                if tax['TaxEvidenceIndicator'] == 'false':
                    tax_exclusive_amount += tax['TaxableAmount']
                    tax_inclusive_amount += tax['TaxAmount']

            data_json = {
                "CustomerInformation": {
                    "IdentificationType": posted_document.partner_id.document_type.key_dian,
                    "Identification": int(posted_document.partner_id.vat),
                    "DV": int(posted_document.partner_id.verification_code),
                    "RegistrationName": posted_document.partner_id.display_name,
                    "CountryCode": posted_document.partner_id.country_id.code,
                    "CountryName": posted_document.partner_id.country_id.name,
                    "SubdivisionCode": int(posted_document.partner_id.state_id.key_dian),
                    "SubdivisionName": posted_document.partner_id.state_id.name,
                    "CityCode": posted_document.partner_id.city_id.key_dian if posted_document.partner_id.country_id.code == "CO" else "",
                    "CityName": posted_document.partner_id.city_id.name,
                    "AddressLine": posted_document.partner_id.street,
                    "Telephone": posted_document.partner_id.phone,
                    "Email": posted_document.partner_id.email,
                    "CustomerCode": posted_document.partner_id.id,
                    "AdditionalAccountID": int(posted_document.partner_id.person_type.key_dian),
                    "TaxLevelCodeListName": int(
                        posted_document.partner_id.property_account_position_id.key_dian.key_dian),
                    "PostalZone": int(posted_document.partner_id.zip),
                    "TaxSchemeCode": "01" if posted_document.partner_id.property_account_position_id.key_dian.key_dian == '48' else 'ZY',
                    "TaxSchemeName": "IVA" if posted_document.partner_id.property_account_position_id.key_dian.key_dian == '48' else 'No causa',
                    "FiscalResponsabilities": self.fiscal_responsabilities(posted_document),
                    "PartecipationPercent": 100,
                    "AdditionalCustomer": []
                },
                "InvoiceGeneralInformation": {
                    "InvoiceAuthorizationNumber": posted_document.journal_id.invoice_resolution.resolution,
                    "PreinvoiceNumber": posted_document.number,
                    "InvoiceNumber": posted_document.number,
                    "DaysOff": posted_document.invoice_payment_term_id.line_ids.days,
                    "Currency": posted_document.currency_id.name,
                    "ExchangeRate": float(posted_document.exchange_rate),
                    "ExchangeRateDate": str(posted_document.invoice_date),
                    "SalesPerson": posted_document.invoice_user_id.name,
                    "Note": "",
                    "ExternalGR": gr,
                    "InvoiceDueDate": (posted_document.date + timedelta(
                        days=posted_document.invoice_payment_term_id.line_ids.days)).strftime("%Y-%m-%d")
                },
                "Delivery": {
                    "AddressLine": "",
                    "CountryCode": "",
                    "CountryName": "",
                    "SubdivisionCode": "",
                    "SubdivisionName": "",
                    "CityCode": "",
                    "CityName": "",
                    "ContactPerson": "",
                    "DeliveryDate": "",
                    "DeliveryCompany": ""
                },
                "AdditionalDocuments": {
                    "OrderReference": "",
                    "DespatchDocumentReference": "",
                    "ReceiptDocumentReference": "",
                    "AdditionalDocument": []
                },
                "AdditionalDocumentReceipt": [],
                "AdditionalProperty": [],
                "PaymentSummary": {
                    "PaymentType": int(posted_document.payment_type_1),
                    "PaymentMeans": int(posted_document.payment_method.key_dian),
                    "PaymentNote": ""
                },
                "ItemInformation": self.load_invoice_line_data_to_json(template_id, posted_document),
                "InvoiceTaxTotal": tax_total,
                "InvoiceAllowanceCharge": [],
                "InvoiceTotal": {
                    "LineExtensionAmount": posted_document.amount_untaxed,
                    "TaxExclusiveAmount": tax_exclusive_amount,
                    "TaxInclusiveAmount": posted_document.amount_untaxed + tax_inclusive_amount,
                    "AllowanceTotalAmount": 0.0,
                    "ChargeTotalAmount": 0.0,
                    "PrePaidAmount": 0,  # posted_document.invoice_payments_widget,
                    "PayableAmount": posted_document.amount_untaxed + tax_inclusive_amount
                    # Deseable calcular los 4 campos
                },
                "Documents": documents
            }

        if template_id == 91:
            tax_total = self.load_invoice_total_tax_to_json(template_id, posted_document)
            tax_exclusive_amount = 0
            tax_inclusive_amount = 0
            for tax in tax_total:
                if tax['TaxEvidenceIndicator'] == 'false':
                    tax_exclusive_amount += tax['TaxableAmount']
                    tax_inclusive_amount += tax['TaxAmount']
            data_json = {
                "CustomerInformation": {
                    "IdentificationType": posted_document.partner_id.document_type.key_dian,
                    "Identification": int(posted_document.partner_id.vat),
                    "DV": int(posted_document.partner_id.verification_code),
                    "RegistrationName": posted_document.partner_id.display_name,
                    "CountryCode": posted_document.partner_id.country_id.code,
                    "CountryName": posted_document.partner_id.country_id.name,
                    "SubdivisionCode": int(posted_document.partner_id.state_id.key_dian),
                    "SubdivisionName": posted_document.partner_id.state_id.name,
                    "CityCode": posted_document.partner_id.city_id.key_dian if posted_document.partner_id.country_id.code == "CO" else "",
                    "CityName": posted_document.partner_id.city_id.name,
                    "AddressLine": posted_document.partner_id.street,
                    "Telephone": posted_document.partner_id.phone,
                    "Email": posted_document.partner_id.email,
                    "CustomerCode": posted_document.partner_id.id,
                    "AdditionalAccountID": int(posted_document.partner_id.person_type.key_dian),
                    "TaxLevelCodeListName": int(
                        posted_document.partner_id.property_account_position_id.key_dian.key_dian),
                    "PostalZone": int(posted_document.partner_id.zip),
                    "TaxSchemeCode": "01" if posted_document.partner_id.property_account_position_id.key_dian.key_dian == '48' else 'ZY',
                    "TaxSchemeName": "IVA" if posted_document.partner_id.property_account_position_id.key_dian == '48' else 'No causa',
                    "FiscalResponsabilities": self.fiscal_responsabilities(posted_document),
                    "PartecipationPercent": 100,
                    "AdditionalCustomer": []
                },
                "NoteGeneralInformation": {
                    "NoteNumber": posted_document.number,
                    "CUFE": posted_document.reversed_entry_id.send_registry.cufe,
                    "ReferenceID": posted_document.reversed_entry_id.name,
                    "IssueDate": posted_document.reversed_entry_id.send_registry.status_date,
                    "CustomizationID": 20,  # 1.1.18 Documento CreditNote
                    "DiscrepancyCode": posted_document.reverse_concept.key_dian,
                    "Currency": posted_document.currency_id.name,
                    "Note": "",
                    "ExternalGR": gr,
                },
                "ItemInformation": self.load_invoice_line_data_to_json(template_id, posted_document),
                "NoteTaxTotal": tax_total,
                "NoteTotal": {
                    "LineExtensionAmount": posted_document.amount_untaxed,
                    "TaxExclusiveAmount": tax_exclusive_amount,
                    "TaxInclusiveAmount": posted_document.amount_untaxed + tax_inclusive_amount,
                    "AllowanceTotalAmount": 0.0,
                    "ChargeTotalAmount": 0.0,
                    "PrePaidAmount": 0,  # posted_document.invoice_payments_widget,
                    "PayableAmount": posted_document.amount_untaxed + tax_inclusive_amount
                },
                "NoteAllowanceCharge": []
            }

        return data_json

    def fiscal_responsabilities(self, posted_document):
        responsibility_con = " "
        for responsibility in posted_document.partner_id.fiscal_responsibility:
            if "R-99-PN" == responsibility.key_dian:
                return responsibility.key_dian
            else:
                responsibility_con = responsibility_con + str(
                    ";" if responsibility_con != " " else " ") + responsibility.key_dian
            return responsibility_con.strip()

    def generate_event_structure(self, posted_document, invoice_result, type_event, reason_id=0):
        structure = {
            "IdentificationType": posted_document.invoice_user_id.document_type.key_dian,
            "Identification": int(posted_document.invoice_user_id.vat),
            "DV": int(posted_document.invoice_user_id.verification_code),
            "RegistrationName": posted_document.invoice_user_id.name,
            "RegitrationLastname": posted_document.invoice_user_id.name,
            "Function": "",
            "Dependence": "",
            "Cufe": invoice_result.cufe,
            "ReceivedDate": invoice_result.status_date,
            "TypeEventID": type_event,
            "ReasonId": reason_id
        }
        return structure

    def insert_event(self, url, token, posted_document, invoice_result, type_event, reason_id=0):
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        url_service = url + "InsertEvent?SchemaID=" + str(schema_id) + "&IDnumber=" + str(id_number)
        payload = self.generate_event_structure(posted_document, invoice_result, type_event, reason_id)
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url_service, headers=headers, json=payload)
        if response.status_code == 400:
            raise exceptions.UserError("Error al insertar el evento: " + "\n\n" + response.json()['Message'])
        print(response.json())

    def insert_invoice(self, url, token, posted_document, gr, documents):
        """
        Función que envia la factura al servicio de Mis Facturas
        @author Julian Valdes - Intello Idea
        @param gr: Representación grafica
        @param url: Base de la url (cambia si es produccion o si es pruebas) donde debe enviar la paeticion de insertar factura
        @param token: Token de acceso
        @param posted_document: Factura
        @param documents: Documentos para el body json
        """
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        template_id = 73
        url_service = url + "InsertInvoice?SchemaID=" + str(schema_id) + "&IDnumber=" + str(
            id_number) + "&TemplateID=" + str(template_id)
        payload = self.load_ed_data_to_json(template_id, posted_document, gr, documents)
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url_service, headers=headers, json=payload)

        detail_send = {
            'date': datetime.now().date(),
            'code_response': response.status_code,
            'message_response': res[response.status_code],
            'type_action': 'send',
            'type_document': 'json',
            'document_filename': 'insert_invoice_' + str(posted_document.id) + '_' + str(
                posted_document.number) + '.json',
            'document': base64.b64encode(bytes(str(json.dumps(payload, sort_keys=True, indent=4)), 'utf-8')),
            'is_attachment': True,
        }
        posted_document.cu_electronic_document_detail_dian(posted_document.id, detail_send, 2)
        posted_document.send_status = True
        if response.status_code == 400:
            raise exceptions.UserError("Error al insertar factura: " + "\n\n" + response.json()['Message'])
        if response.status_code == 200:
            time.sleep(2)
            electronic_document = self.get_electronic_document(url, token, posted_document,
                                                               response.json()['DocumentId'], document_type=1)
            json_electronic = electronic_document.json()
            detail_invoice = {
                'cufe': json_electronic['CUFE'],
                'document_key': response.json()['DocumentId'],
                'status_date': json_electronic['StatusDate'],
            }
            detail_send = {
                'date': datetime.now().date(),
                'code_response': electronic_document.status_code,
                'message_response': res[electronic_document.status_code],
                'type_action': 'validation',
                'type_document': 'json',
                'document_filename': 'status_invoice_' + str(posted_document.id) + '_' + str(
                    posted_document.number) + '.json',
                'document': base64.b64encode(
                    bytes(str(json.dumps(json_electronic, sort_keys=True, indent=4)), 'utf-8')),
                'is_attachment': False,
            }
            send_registry = posted_document.cu_electronic_document_dian(posted_document.id, detail_invoice, 3)
            posted_document.cu_electronic_document_detail_dian(posted_document.id, detail_send, 2)
            posted_document.validate_status = True

    def insert_note(self, url, token, posted_document, gr):
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        note_type = 91
        url_service = url + "insertnote?SchemaID=" + str(schema_id) + "&IDnumber=" + str(
            id_number) + "&NoteType=" + str(note_type)
        payload = self.load_ed_data_to_json(note_type, posted_document, gr, [])
        json_doc = json.dumps(payload, indent=4)

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url_service, headers=headers, json=payload)

        detail_send = {
            'date': datetime.now().date(),
            'code_response': response.status_code,
            'message_response': res[response.status_code],
            'type_action': 'send',
            'type_document': 'json',
            'document_filename': 'insert_invoice_' + str(posted_document.id) + '_' + str(
                posted_document.number) + '.json',
            'document': base64.b64encode(bytes(str(json.dumps(payload, sort_keys=True, indent=4)), 'utf-8')),
            'is_attachment': True,
        }
        posted_document.cu_electronic_document_detail_dian(posted_document.id, detail_send, 2)

        if response.status_code == 400:
            raise exceptions.UserError("Error al insertar la nota: " + "\n\n" + response.json()['Message'])

        if response.status_code == 200:
            time.sleep(2)
            electronic_document = self.get_electronic_document(url, token, posted_document,
                                                               response.json()['DocumentId'], document_type=2)
            json_electronic = electronic_document.json()
            detail_invoice = {
                'cufe': json_electronic['CUFE'],
                'document_key': response.json()['DocumentId'],
                'status_date': json_electronic['StatusDate'],
            }
            detail_send = {
                'date': datetime.now().date(),
                'code_response': electronic_document.status_code,
                'message_response': res[electronic_document.status_code],
                'type_action': 'validation',
                'type_document': 'json',
                'document_filename': 'status_invoice_' + str(posted_document.id) + '_' + str(
                    posted_document.number) + '.json',
                'document': base64.b64encode(
                    bytes(str(json.dumps(json_electronic, sort_keys=True, indent=4)), 'utf-8')),
                'is_attachment': False,
            }

            send_registry = posted_document.cu_electronic_document_dian(posted_document.id, detail_invoice, 3)
            posted_document.cu_electronic_document_detail_dian(posted_document.id, detail_send, 2)
        else:
            raise exceptions.ValidationError(response.text.split('"')[3])

    def get_electronic_document(self, url, token, posted_document, document_id, document_type):
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        url_service = url + "GetDocumentStatus?SchemaID=" + str(schema_id) + "&IDNumber=" + str(
            id_number) + "&DocumentId=" + str(document_id) + "&DocumentType=" + str(document_type)
        payload = {}
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url_service, headers=headers, data=payload)
        return response

    def attach_rg(self, url, token, posted_document, b64):
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        document_id = posted_document.send_registry.document_key
        document_type = 1 if posted_document.type == "out_invoice" else 2
        url_service = url + "AttachRG?SchemaID=" + str(schema_id) + "&IDNumber=" + str(
            id_number) + "&DocumentId=" + str(document_id) + "&DocumentType=" + str(document_type)
        payload = {}
        files = [
            ('File', base64.decodebytes(b64))
        ]
        headers = {
            'Authorization': token,
        }
        response = requests.request("POST", url_service, headers=headers, data=payload, files=files)
        detail_send = {
            'date': datetime.now().date(),
            'code_response': response.status_code,
            'message_response': res[response.status_code],
            'type_action': 'gr',
            'type_document': 'pdf',
            'document_filename': '',
            'document': '',
            'is_attachment': False,
        }
        posted_document.cu_electronic_document_detail_dian(posted_document.id, detail_send, 4)

    def insert_attachment(self, url, token, posted_document, file):
        schema_id = posted_document.company_id.partner_id.document_type.key_dian
        id_number = posted_document.company_id.partner_id.vat
        url_service = url + "InsertAttachment?SchemaID=" + str(schema_id) + "&IDNumber=" + str(id_number)
        payload = {}
        files = file
        headers = {
            'Authorization': token,
        }
        response = requests.request("POST", url_service, headers=headers, data=payload, files=files)
        detail_send = {
            'date': datetime.now().date(),
            'code_response': response.status_code,
            'message_response': res[response.status_code],
            'type_action': 'attachment',
            'type_document': None,
            'document_filename': None,
            'document': None,
            'is_attachment': False,
        }
        return_data = [response.json(), detail_send]
        return return_data

    def send_electronic_document(self, posted_document):
        parameter = self._get_parameters_connection()
        parameter_settings = self._get_parameters_settings()
        send = None
        if posted_document.type == 'out_invoice':
            list_document_invoice = self.get_document_attachment(parameter['url'], parameter['token'], posted_document)
            send = self.insert_invoice(parameter['url'], parameter['token'], posted_document,
                                       parameter_settings['fe_own_gr'], list_document_invoice)

        if posted_document.type == 'out_refund':
            send = self.insert_note(parameter['url'], parameter['token'], posted_document,
                                    parameter_settings['fe_own_gr'])

        return send

    def send_event_document(self, posted_document, type_event, reason_id=0):
        parameter = self._get_parameters_connection()
        parameter_settings = self._get_parameters_settings()
        send = None
        # if posted_document.type == 'out_invoice':
        invoice_result = self.env['electronic.document.dian'].search([('invoice', '=', posted_document.id)])
        print(invoice_result['document_key'])
        invoice_result_status_from_mis_facturas = self.get_electronic_document(parameter['url'], 
                                                                               parameter['token'], 
                                                                               posted_document, 
                                                                               invoice_result['document_key'], 
                                                                               1)
        if invoice_result_status_from_mis_facturas.status_code == 400:
            raise exceptions.ValidationError("No se pudo obtener la informacion de la factura")
        invoice_result_status_from_mis_facturas = invoice_result_status_from_mis_facturas.json()
        if not invoice_result_status_from_mis_facturas['CUFE']:
            raise exceptions.ValidationError("Aún no se ha de la factura")
        invoice_result['cufe'] = invoice_result_status_from_mis_facturas['CUFE']
        send = self.insert_event(parameter['url'], parameter['token'], posted_document, invoice_result, type_event,
                                 reason_id)
        return send

    def send_rg_electronic_document(self, b64, posted_document):
        parameter = self._get_parameters_connection()
        self.attach_rg(parameter['url'], parameter['token'], posted_document, b64)

    def get_document_attachment(self, url, token, posted_document):
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.move'), ('res_id', '=', posted_document.id)])
        list_document_invoice = []
        for attach in attachments:
            list_tup_file = [(attach.name, base64.decodebytes(attach.datas))]
            file_attach = self.insert_attachment(url, token, posted_document, list_tup_file)
            print(str(file_attach))
            dic_file = {'Name': file_attach[0]['FileMailBoxList'][0]['FileName'],
                        'ID': file_attach[0]['FileMailBoxList'][0]['FileMailBoxUUID']}
            attach.update({
                'fe_filename': file_attach[0]['FileMailBoxList'][0]['FileName'],
                'fe_file_code': file_attach[0]['FileMailBoxList'][0]['FileMailBoxUUID']
            })
            file_attach[1]['type_document']: attach.mimetype.split("/")[1]
            file_attach[1]['document_filename']: attach.name
            file_attach[1]['document']: attach.datas
            list_document_invoice.append(dic_file)
            print(file_attach[1])
            posted_document.cu_electronic_document_detail_dian(posted_document.id, file_attach[1], 1)

        return list_document_invoice
