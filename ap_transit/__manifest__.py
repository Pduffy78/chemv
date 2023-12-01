# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Ap Transit",
    "version" : "14.00",
    "summary": "Ap Transit",
    "sequence": 1,
    "description": """ Ap Transit """,
    "category": "Product",
    "website": "http://ap-accounting.co.za",
    "depends" : ["base",
                 "sale_management",
                 "stock",
                 "purchase",
                 ],
    "data": [
            "views/stock_picking_view.xml",
            ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

