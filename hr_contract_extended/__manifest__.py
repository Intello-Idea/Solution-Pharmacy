# -*- coding: utf-8 -*-

{
    'name': 'Contract Extended',
    'summary': 'Se extiende funcionalidad de contratos',
    'version': '13-15',
    'category': 'Human Resources',
    'website': 'https://www.endtoendt.com/',
    'author': 'End to End Technology by Cesar Quiroga',
    'license': '',
    'application': False,
    'installable': True,
    'depends': [
        'hr_contract',
        'hr',
        ],
    'description': 'Se extiende funcionalidad de los contractos para que manejar la tasa de riesgo profesional y entidades relacionadas al empleado (EPS, ARL, ect.)',
    'data': [
        'views/hr_risk_view.xml',
        'views/hr_contract_view.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ]
}
