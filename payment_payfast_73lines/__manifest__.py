# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'PayFast Payment Acquirer',
    'category': 'Payment Gateway',
    'summary': 'Payment Acquirer: PayFast Implementation',
    'version': '18.0',
    'author': '73Lines',
    'description': """PayFast Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payfast.xml',
        'views/payment_acquirer.xml',
        'data/payfast.xml'
    ],
    'images': [
        'static/description/payfast_payment_gateway_banner.png',
    ],
    'price': 0,
    'license': 'Other proprietary',
    'currency': 'EUR',
}
