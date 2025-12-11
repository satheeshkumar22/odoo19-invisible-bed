# -*- coding: utf-8 -*-

{
    'name': "Accounts Extended",
    'author': 'Navabrind IT solutions',
    'category': 'account',
    'summary': """Customization on Account model""",
    'website': '',
    'description': """""",
    'version': '19.0.1.0.0',
    'depends': ['base','account','sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/cron.xml',
        'views/account_move.xml',
        'views/account_account.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'wizard/account_sale_advance_payment.xml',
        'wizard/account_purchase_advance_payment.xml'
       ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
