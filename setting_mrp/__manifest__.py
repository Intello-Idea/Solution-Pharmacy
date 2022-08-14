# -*- coding: utf-8 -*-
{
    'name': "Setting Mrp",

    'description': """
                Módulo Setting Mrp modifica: 
                    1. Orden de Producción agregando campos nuevos en la ficha de Orden de Producción
                    2. Creación reporte QWEB-PDF llamado Orden de Producción dentro de Orden de Producción
    """,
    #Si colocan nueva funcionalidad dentro de esté modulo por favor agregarlo al resumén
    #para tener la documentación al día, además de comentar las modificaciones realizadas
    'summary': 'Modulo desarrollado para las modificación en el módulo de fabricación',
    'author': "Intello Idea - Developer-Routh Milano 28-04-2022",
    'website': "http://www.intelloidea.com",
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',
    'depends': ['base', 'base_epithelium', 'custom_contact','mrp'],
    'application': False,
    'data': [
        #agregar data antes del security sólo si existe o se requiere
        'security/ir.model.access.csv',
        'report/production_order_template.xml',
        'report/product_identification_in_process.xml',
        'views/mrp_production_view.xml',
        'views/mrp_bom.xml',
        #agregar wizard despues de views sólo si existe o se requiere
    ],

}
