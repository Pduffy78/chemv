# -*- coding: utf-8 -*-
{
    'name': "batch_payment",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2.4',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
            'security/res_security.xml',
            'views/batch_payment.xml',
            'reports/batch_payment_pdf.xml',
            'wizard/ix_batch_payment_xls.xml',
            'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
