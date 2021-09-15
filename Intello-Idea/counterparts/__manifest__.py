{
    'name': "counterparts",
    'summary': """counterparts""",
    'description': """
        Module for partner category
    """,
    'author': "Intello Idea SAS",
    'website': "http://intelloidea.com/",
    'category': 'Partner',
    'version': '1.0',

    'depends': ['base', 'base_setup', 'product', 'sale', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/inventory_counterparts_tab.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'report/stock_move_report.xml'
    ],
}
