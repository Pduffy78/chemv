# -*- coding: utf-8 -*-
# from odoo import http


# class V15MrpTack(http.Controller):
#     @http.route('/v15_mrp_tack/v15_mrp_tack', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/v15_mrp_tack/v15_mrp_tack/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('v15_mrp_tack.listing', {
#             'root': '/v15_mrp_tack/v15_mrp_tack',
#             'objects': http.request.env['v15_mrp_tack.v15_mrp_tack'].search([]),
#         })

#     @http.route('/v15_mrp_tack/v15_mrp_tack/objects/<model("v15_mrp_tack.v15_mrp_tack"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('v15_mrp_tack.object', {
#             'object': obj
#         })
