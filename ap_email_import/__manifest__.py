# -*- encoding: utf-8 -*-
{
    'name': 'AP Email Import',
    'category': 'Email',
    'version': '18.1',
    'depends': ['mass_mailing'],
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



