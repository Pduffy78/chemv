# -*- coding: utf-8 -*-
# from odoo import http


# class BatchPayment(http.Controller):
#     @http.route('/batch_payment/batch_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/batch_payment/batch_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('batch_payment.listing', {
#             'root': '/batch_payment/batch_payment',
#             'objects': http.request.env['batch_payment.batch_payment'].search([]),
#         })

#     @http.route('/batch_payment/batch_payment/objects/<model("batch_payment.batch_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('batch_payment.object', {
#             'object': obj
#         })
