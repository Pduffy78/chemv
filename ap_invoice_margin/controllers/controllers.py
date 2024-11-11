# -*- coding: utf-8 -*-
# from odoo import http


# class ApInvoiceMargin(http.Controller):
#     @http.route('/ap_invoice_margin/ap_invoice_margin', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ap_invoice_margin/ap_invoice_margin/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ap_invoice_margin.listing', {
#             'root': '/ap_invoice_margin/ap_invoice_margin',
#             'objects': http.request.env['ap_invoice_margin.ap_invoice_margin'].search([]),
#         })

#     @http.route('/ap_invoice_margin/ap_invoice_margin/objects/<model("ap_invoice_margin.ap_invoice_margin"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ap_invoice_margin.object', {
#             'object': obj
#         })
