# -*- coding: utf-8 -*-
{
    'name': "Account Follow up Extended",

    'summary': """
    Extended Account follow up module to allow to show partner child ids records when we fetch follow report
        """,

    'description': """
        Extended Account follow up module to allow to show partner child ids records when we fetch follow report
    """,

    'author': "AP Accounting",
    'website': "ap-systems.co.za",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account Reports',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_followup'],

    # always loaded
    'data': [
        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}