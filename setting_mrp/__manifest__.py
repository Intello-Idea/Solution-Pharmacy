# -*- coding: utf-8 -*-
{
    'name': "Setting Mrp",

    'description': 'Modulo desarrollado para las modificación en el módulo de fabricación',
    #Si colocan nueva funcionalidad dentro de esté modulo por favor agregarlo al resumén
    #para tener la documentación al día, además de comentar las modificaciones realizadas
    'summary': """Módulo Setting Mrp modifica: 
                    1. Orden de Producción agregando campos nuevos en la ficha de Orden de Producción
                """,
    'author': "Intello Idea - Developer-Routh Milano 28-04-2022",
    'website': "http://www.intelloidea.com",
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',
    'depends': ['base', 'base_epithelium', 'custom_contact','mrp'],
    'data': [
        #agregar data antes del security si edxiste
        'security/ir.model.access.csv',
        #agregar report antes de views si existe
        'views/mrp_production_view.xml',
        #agregar wizard despues de views si existe
    ],

}
