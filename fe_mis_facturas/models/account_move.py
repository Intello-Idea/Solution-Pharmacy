from odoo import api, fields, models, _, exceptions


class AccountMove(models.Model):
    _inherit = 'account.move'

    def send_document(self):
        super(AccountMove, self).send_document()
        fe_methods = self.env['fe.mf.methods']
        fe_methods.send_electronic_document(self)

    def insert_event_dian_acknowledgment(self):
        super(AccountMove, self).insert_event_dian_acknowledgment()
        fe_methods = self.env['fe.mf.methods']
        fe_methods.send_event_document(self, 1)
        self.electronic_document_event_status = '1'

    def insert_event_dian_acceptance(self):
        super(AccountMove, self).insert_event_dian_received()
        fe_methods = self.env['fe.mf.methods']
        fe_methods.send_event_document(self, 2)
        self.electronic_document_event_status = '2'

    def insert_event_dian_claim(self):
        super(AccountMove, self).insert_event_dian_received()
        view = self.env.ref('fe_mis_facturas.view_send_event_invoice')
        # TDE FIXME: a return in a loop, what a good idea. Really.
        context = self._context.copy()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'send.event.invoice.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def insert_event_dian_received(self):
        super(AccountMove, self).insert_event_dian_received()
        fe_methods = self.env['fe.mf.methods']
        fe_methods.send_event_document(self, 4)
        self.electronic_document_event_status = '4'

    def send_gr_document(self, b64):
        fe_methods = self.env['fe.mf.methods']
        fe_methods.send_rg_electronic_document(b64, self)
        self.update_electronic_document_status(6)

    def cron_electronic_invoice(self):
        invoices = super(AccountMove, self).cron_electronic_invoice()
        fe_methods = self.env['fe.mf.methods']
        parameter = fe_methods._get_parameters_connection()
        parameter_settings = fe_methods._get_parameters_settings()

        if invoices:
            for invoice in invoices:
                if invoice.electronic_document_status != 0:
                    # invoice_electronic = fe_methods.send_electronic_document(invoice)
                    status_document = fe_methods.get_electronic_document(parameter['url'], parameter['token'], invoice,
                                                                         invoice.send_registry.document_key,
                                                                         document_type=1)
                    print(status_document['DocumentStatus'])
