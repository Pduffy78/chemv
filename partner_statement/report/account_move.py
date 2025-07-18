from odoo import _, api, models,fields


class AccountMoveLine(models.Model):
    """Model of Activity Statement"""

    _inherit = "account.move.line"

    blocked = fields.Boolean(string="Blocked",compute="_compute_blocked",store=True)

    @api.depends('move_id.payment_state')
    def _compute_blocked(self):
        for rec in self:
            if rec.move_id.payment_state == 'Blocked':
                rec.blocked == True
            else:
                rec.blocked == False