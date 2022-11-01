# -*- coding: utf-8 -*-
{
    'name': "Referido",

    'description': """
       Agregar campos referidos a diferentes vistas y modelos
    """,
    'author': "Intello Idea",
    'website': "https://intello-idea.odoo.com/",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'sale', 'quotator', 'account'],

    'data': [
        'views/account_view.xml',
        'views/quotator_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
    ],
}