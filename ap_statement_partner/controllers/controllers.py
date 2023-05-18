# -*- coding: utf-8 -*-
# from odoo import http


# class ApStatementPartner/home/bhavya/server/v15/apStatementPartner(http.Controller):
#     @http.route('/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ap_statement_partner/home/bhavya/server/v15/ap_statement_partner.listing', {
#             'root': '/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner',
#             'objects': http.request.env['ap_statement_partner/home/bhavya/server/v15/ap_statement_partner.ap_statement_partner/home/bhavya/server/v15/ap_statement_partner'].search([]),
#         })

#     @http.route('/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/ap_statement_partner/home/bhavya/server/v15/ap_statement_partner/objects/<model("ap_statement_partner/home/bhavya/server/v15/ap_statement_partner.ap_statement_partner/home/bhavya/server/v15/ap_statement_partner"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ap_statement_partner/home/bhavya/server/v15/ap_statement_partner.object', {
#             'object': obj
#         })
