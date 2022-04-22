# -*- coding: utf-8 -*-
{
    'name': 'Employee Extended',
    'version': '13-15',
    'summary': """Adición de campos avanzados en el maestro de empleados""",
    'description': 'Este módulo te ayuda a agregar más información en los registros de los empleados.',
    'category': 'Generic Modules/Human Resources',
    'author': 'End to End Technology by Cesar Quiroga',
    'website': "https://www.endtoendt.com/",
    'depends': ['base', 'hr', 'mail', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_employee_view.xml',
    ],
    'demo': [],
    'license': '',
    'installable': True,
    'auto_install': False,
    'application': False,
}
