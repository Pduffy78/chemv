{'name': "Debtor Import", 
        'summary': "",
       'version': "1.4",
       'depends': ['base','sale'],
       'author': "AP Accounting Services",
       'license': '',
       'website': "http://www.ap-accounting.co.za",
       'category': 'Purchase',
       'description': """
    
    """,
       'data': [
                'wizard/import_wizard.xml',
                'wizard/account_view.xml',
                'wizard/debtor_issue.xml',
                'security/ir.model.access.csv',
        ],
       'qweb': [ 
           
           
           ],
       'sequence': 10,
       'installable': True ,
       'auto_install':  False,
       }

