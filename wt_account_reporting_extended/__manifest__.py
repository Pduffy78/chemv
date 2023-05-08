# -*- coding: utf-8 -*-

{
    "name" : "wt account reporting",
    "version" : "13.0.0.1",
    "category" : "Accounting",
    'summary': 'account trial balance extended with account filter',
    "description": """
        wt account reporting with account filter
    """,
    "author": "Warlock Technologies Pvt Ltd.",
    "website" : "http://warlocktechnologies.com",
    "depends" : ['account_reports'],
    "data": [
        'views/search_template_view_extended.xml',
        # 'views/assets.xml',
    ],
    'qweb': [],
    'assets':{'web.assets_backend' : ['wt_account_reporting_extended/static/src/scss/custom.scss']},
    "auto_install": False,
    "installable": True,
}