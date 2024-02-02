# -*- coding: utf-8 -*-
{
    'name': "Real Estate",

    'summary': """
        Real Estate Advertisement module""",

    'description': """
        A module made to manage a database of households.
    """,

    'author': "Alejandro Nebot Flores",
    'website': "https://odoo.com",

    'category': 'Sales/RealEstate',
    'version': '1.0',

    'depends': ['base'],

    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
    'installable':True,
    'auto_install':False
}
