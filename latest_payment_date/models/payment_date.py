from odoo import models, fields, api,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    latest_paymn_date = fields.Date(string='Latest Payment Date',compute='_compute_latest_payment_date',store=True)
    update_payment_date = fields.Boolean(string='Latest Payment Date Update', default = False)
    
    
    @api.depends('move_type', 'line_ids.amount_residual','payment_state', 'update_payment_date')
    def _compute_latest_payment_date(self):
        for move in self:
            list_date = []
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            if move.move_type == 'out_invoice' and  move.state == 'posted' and move.is_invoice(include_receipts=True):
                for data in move._get_reconciled_info_JSON_values():
                    list_date.append(data.get('date'))
                if list_date:
                    move.latest_paymn_date = max(list_date)
            else:
                move.latest_paymn_date = False
    
    
    def update_payment_date_update(self):
        for rec in self:
            rec.update_payment_date = True
