# -*- coding: utf-8 -*-
# from odoo import http


# class ApSales(http.Controller):
#     @http.route('/ap_sales/ap_sales', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ap_sales/ap_sales/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ap_sales.listing', {
#             'root': '/ap_sales/ap_sales',
#             'objects': http.request.env['ap_sales.ap_sales'].search([]),
#         })

#     @http.route('/ap_sales/ap_sales/objects/<model("ap_sales.ap_sales"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ap_sales.object', {
#             'object': obj
#         })
