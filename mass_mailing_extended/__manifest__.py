# -*- coding: utf-8 -*-
{
    'name': "Mass MAiling Extended",

    'summary': """ 
    """,

    'description': """
    """,

    'author': "AP Accounting",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Mass Mailing',
    'version': '18.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mass_mailing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mass_mailing.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
