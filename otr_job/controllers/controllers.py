# -*- coding: utf-8 -*-
# from odoo import http


# class OtrJob(http.Controller):
#     @http.route('/otr_job/otr_job', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/otr_job/otr_job/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('otr_job.listing', {
#             'root': '/otr_job/otr_job',
#             'objects': http.request.env['otr_job.otr_job'].search([]),
#         })

#     @http.route('/otr_job/otr_job/objects/<model("otr_job.otr_job"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('otr_job.object', {
#             'object': obj
#         })
