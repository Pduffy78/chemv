# -*- coding: utf-8 -*-
# from odoo import http


# class V15InvoiceCreation(http.Controller):
#     @http.route('/v15_invoice_creation/v15_invoice_creation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/v15_invoice_creation/v15_invoice_creation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('v15_invoice_creation.listing', {
#             'root': '/v15_invoice_creation/v15_invoice_creation',
#             'objects': http.request.env['v15_invoice_creation.v15_invoice_creation'].search([]),
#         })

#     @http.route('/v15_invoice_creation/v15_invoice_creation/objects/<model("v15_invoice_creation.v15_invoice_creation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('v15_invoice_creation.object', {
#             'object': obj
#         })
