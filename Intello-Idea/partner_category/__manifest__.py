{
    'name': "Partner Category",
    'summary': """Partner Category""",
    'description': """
        Module for partner 
    """,
    'author': "Intello Idea SAS",
    'website': "http://intelloidea.com/",
    'category': 'Partner',
    'version': '1.0',
    'depends': ['base', 'l10n_co', 'base_setup','sale_management','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_category_intello.xml',
        'views/sale_order_intello.xml',
        'views/marketing_activities.xml',
    ],
}
