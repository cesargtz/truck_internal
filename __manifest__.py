# -*- coding: utf-8 -*-
{
    'name': "truck_internal",

    'summary': """
       View for Truck Transfer""",

    'description': """
       
    """,

    'author': "Yecora",
    'website': "http://www.yecora.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'warehouse',
    'version': '10.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
	        	'truck',
	        	'truck_transfer'],

    # always loaded
    'data': [
        'security/truck_internal_access_rules.xml',
        'security/ir.model.access.csv',
        'views/truck_internal.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
