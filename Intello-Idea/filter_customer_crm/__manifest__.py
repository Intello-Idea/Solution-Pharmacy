{
    'name': "Filter Customer CRM",
    'summary': """Filter Customer CRM""",
    'description': """
       Module to fix crm customer filter
    """,
    'author': "Intello Idea SAS",
    'website': "http://intelloidea.com/",
    'category': 'Fix',
    'version': '1.0',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_view.xml',
    ],
}
