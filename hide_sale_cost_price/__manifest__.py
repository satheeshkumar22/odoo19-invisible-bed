# -*- coding: utf-8 -*-

{
    'name': "Hide Sale and Cost Price of the Product",
    'author': 'Navabrind IT solutions',
    'category': 'Sales',
    'summary': """Hide Sale and Cost Price of the Product""",
    'website': '',
    'description': """This module allows hiding sale and cost prices of products.""",
    'version': '19.0.1.0.0',
    'depends': ['base','product'],
    'data': [
        'security/security.xml',
        'views/product_template.xml'
           ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
