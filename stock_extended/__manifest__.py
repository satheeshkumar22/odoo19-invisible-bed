# -*- coding: utf-8 -*-

{
    'name': "Inventory Extended",
    'author': 'Navabrind IT solutions',
    'category': 'stock',
    'summary': """Customization on Account model""",
    'website': '',
    'description': """""",
    'version': '19.0.1.0.0',
    'depends': ['base','stock','sale_stock'],
    'data': [
        'data/mail_template.xml',
        'views/stock_picking.xml',
       ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
