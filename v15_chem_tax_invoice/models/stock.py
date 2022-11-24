import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero


# class StockQuant(models.Model):
#     _inherit = 'stock.quant'
#
#
#     @api.model
#     def action_view_inventory(self):
#         """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
#         self = self._set_view_context()
#         self._quant_tasks()
#
#         ctx = dict(self.env.context or {})
#         ctx['no_at_date'] = True
#         if self.user_has_groups('stock.group_stock_user') and not self.user_has_groups('stock.group_stock_manager'):
#             ctx['search_default_my_count'] = True
#         action = {
#             'name': _('Inventory Adjustments'),
#             'view_mode': 'tree,form',
#             'views': [(self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,'tree'),
#                         (self.env.ref('stock.view_stock_quant_form_editable').id, 'form')],
#             'res_model': 'stock.quant',
#             'type': 'ir.actions.act_window',
#             'context': ctx,
#             'domain': [('location_id.usage', 'in', ['internal', 'transit'])],
#             'help': """
#                 <p class="o_view_nocontent_smiling_face">
#                     {}
#                 </p><p>
#                     {} <span class="fa fa-long-arrow-right"/> {}</p>
#                 """.format(_('Your stock is currently empty'),
#                            _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
#                            _('Import')),
#         }
#         return action