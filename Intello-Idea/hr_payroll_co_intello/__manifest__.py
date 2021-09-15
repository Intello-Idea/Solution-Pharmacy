# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll Intello",

    'description': 'Modulo de nomina para Odoo13',
    # Long description of module's purpose

    'summary': 'Nomina Odooo',
    # Short (1 phrase/line) summary of the module's purpose, used as
    # subtitle on modules listing or apps.openerp.com""",

    'author': "Intello Idea",
    'website': "http://www.intelloidea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'ln10_co_intello', 'hr_contract', 'hr_payroll'],
    'application': False,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/risk_work_data.xml',
        'data/cotizante_type_data.xml',
        'data/cotizante_subtype_data.xml',
        'data/hr_concept_data.xml',
        'data/hr_change_control_data.xml',
        'data/hr_reason_change_data.xml',
        'data/hr_payroll_type_data.xml',
        'data/hr_novelty_data.xml',
        'data/hr_loan_data.xml',
        'wizard/hr_change_control_wizard.xml',
        'report/hr_loan_reports.xml',
        'report/loan_employee_report.xml',
        'report/loan_employee_status_report.xml',
        'views/risk_work_views.xml',
        'views/res_partner_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_change_reason_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_concept_fixed_views.xml',
        'views/hr_payroll_views.xml',
        'views/hr_novelty_views.xml',
        'views/hr_loan_views.xml',
        'views/menuitems_views.xml',

    ],

    # only loaded in demonstration mode
    # 'demo': [
    # ],
}
