# -*- coding: utf-8 -*-
{
    'name': "Quotaror",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Intello Idea",
    'website': "https://intello-idea.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'product', 'sale', 'sale_management', 'stock', 'base_solution', 'contacts_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/quotator.xml',
        'views/purchase_order.xml',
        'security/groups_security.xml',
        'views/sale_order.xml',
        'data/ir_sequence_data.xml',
        'reports/sale_report_templates.xml',
        'views/discount_rates.xml',
        'wizard/send_sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
