# -*- coding: utf-8 -*-
{
    'name': "Bonificate_products",
    'summary': """Bonification products""",
    'description': """
        Module
    """,
    'author': "Intello Idea SAS",
    'website': "http://intelloidea.com/",
    'category': 'Partner',
    'version': '1.0',

    'depends': ['partner_category', 'sale'],

    'data': ['security/ir.model.access.csv',
             'views/sale_order_view.xml',
             'views/account_view.xml',
             'reports/sale_report_templates.xml',
             ],

}
