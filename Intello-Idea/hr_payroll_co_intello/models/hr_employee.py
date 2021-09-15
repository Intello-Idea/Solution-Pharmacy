from odoo import api, fields, models, exceptions, _

DOCUMENT_TYPE = [('rut', 'NIT'),
                 ('id_document', 'Cédula'),
                 ('id_card', 'Tarjeta de Identidad'),
                 ('passport', 'Pasaporte'),
                 ('foreign_id_card', 'Cédula Extranjera'),
                 ('external_id', 'ID del Exterior'),
                 ('diplomatic_card', 'Carné Diplomatico'),
                 ('residence_document', 'Salvoconducto de Permanencia'),
                 ('civil_registration', 'Registro Civil'),
                 ('national_citizen_id', 'Cédula de ciudadanía')]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    odoo_contact = fields.Many2one('res.partner', 'Odoo Contact')
    document_type = fields.Many2one('ln10_co_intello.documenttype', 'Document Type',
                                    related='odoo_contact.document_type')

    """Inherit Field"""
    identification_id = fields.Char('Identification No', related='odoo_contact.vat')


class HrCotizanteType(models.Model):
    _name = 'hr.cotizante.type'
    _description = 'Model Cotizante Type for employee'

    name = fields.Char('Cotizante Type', help='Name of Type of Contributor')
    code = fields.Integer('Code')
    is_active = fields.Boolean('Active')

    eps = fields.Boolean('EPS', help='Health Care Provider')
    arl = fields.Boolean('ARL', help='Occupational Risk Manager')
    afp = fields.Boolean('AFP', help='Pension and severance fund administrator')
    ccf = fields.Boolean('CCF', help='Family Compensation Fund')
    sena = fields.Boolean('SENA', help='Servicio Nacional de Aprendizaje')
    icbf = fields.Boolean('ICBF', help='Instituto Colombiano de Bienestar Familiar')

    description = fields.Text('Description')

    cotizante_subtyṕe_ids = fields.Many2many('hr.cotizante.subtype', 'hr_cotizante_type_subtype', 'type_id',
                                             'subtype_id', 'Cotizante Subtypes')

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            if rec.code > 99:
                raise exceptions.ValidationError(_('The code cannot be longer than two digits.'))


class HrCotizanteSubType(models.Model):
    _name = 'hr.cotizante.subtype'
    _description = 'Cotizante Sub Type for Type cotizante'

    name = fields.Char('Cotizante Subtype', help='Contributor Subtype Name')
    code = fields.Integer('Code')
    is_active = fields.Boolean('Active', default=False)
    description = fields.Text('Description')

    cotizante_type_ids = fields.Many2many('hr.cotizante.type', 'hr_cotizante_type_subtype', 'subtype_id', 'type_id',
                                          string='Cotizante Subtype')

    active = fields.Boolean('Active', default=True)

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            if rec.code > 99:
                raise exceptions.ValidationError(_('The code cannot be longer than two digits.'))
