# -*- coding: utf-8 -*-

{
    'name': "MRP Extended",
    'author': 'Navabrind IT solutions',
    'category': 'sales',
    'summary': """Customization on Manufactoring model""",
    'website': '',
    'description': """""",
    'version': '19.0.1.0.0',
    'depends': ['base', 'mrp', 'stock', 'sale', 'product','account'],
    'data': [
        'data/mail_data.xml',
        'data/mo_reminder_cron.xml',
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/work_order_views.xml',
        'views/res_settings.xml'
       ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
