# -*- encoding: utf-8 -*-
{
    'name': 'AP Email Import',
    'category': 'Email',
    'version': '15.0',
    'depends': ['base','mass_mailing','mass_mailing_extended'],
    'description': """AP Email Import""",
    'data': [
              'security/ir.model.access.csv',
              'wizard/email_import_view.xml',
            ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}



