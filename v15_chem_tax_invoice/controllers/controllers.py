# -*- coding: utf-8 -*-
# from odoo import http


# class V15BestgroupImportInvoice(http.Controller):
#     @http.route('/v15_bestgroup_import_invoice/v15_bestgroup_import_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/v15_bestgroup_import_invoice/v15_bestgroup_import_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('v15_bestgroup_import_invoice.listing', {
#             'root': '/v15_bestgroup_import_invoice/v15_bestgroup_import_invoice',
#             'objects': http.request.env['v15_bestgroup_import_invoice.v15_bestgroup_import_invoice'].search([]),
#         })

#     @http.route('/v15_bestgroup_import_invoice/v15_bestgroup_import_invoice/objects/<model("v15_bestgroup_import_invoice.v15_bestgroup_import_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('v15_bestgroup_import_invoice.object', {
#             'object': obj
#         })
