# -*- coding: utf-8 -*-
# from odoo import http


# class ManualOperationVisible(http.Controller):
#     @http.route('/manual_operation_visible/manual_operation_visible', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manual_operation_visible/manual_operation_visible/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('manual_operation_visible.listing', {
#             'root': '/manual_operation_visible/manual_operation_visible',
#             'objects': http.request.env['manual_operation_visible.manual_operation_visible'].search([]),
#         })

#     @http.route('/manual_operation_visible/manual_operation_visible/objects/<model("manual_operation_visible.manual_operation_visible"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manual_operation_visible.object', {
#             'object': obj
#         })
