# -*- coding: utf-8 -*-
{
    'name': "bonification_solution",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """ 
        module that includes everything related to subsidies
    """,

    'author': "Intello Idea",
    'website': "http://www.intello-idea.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/rate_bonification.xml',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
