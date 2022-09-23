from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    amount_credit_limit = fields.Monetary(string='Internal Credit Limit', default=-1)
    credit_limit_compute = fields.Monetary(
        string='Credit Limit ', default=-1,
        compute='_compute_credit_limit_compute', inverse='_inverse_credit_limit_compute',
        help='A limit of zero means no limit. A limit of -1 will use the default (company) limit.'
    )
    show_credit_limit = fields.Boolean(compute='_compute_show_credit_limit')
    account_credit_limit = fields.Boolean(
        string="Sales Credit Limit", readonly=False,
        help="ETrigger alerts when creating Invoices and Sales Orders for Partners with a Total Receivable amount exceeding a limit.")
    account_default_credit_limit = fields.Monetary(
        string="Default Credit Limit", readonly=False,
        help="A limit of zero means no limit by default.")
    credit_limit_type = fields.Selection([('warning', 'Warning'), ('block', 'Block')],string="Credit Limit Type", 
                                         readonly=False)
    compute_credit_limit_type = fields.Selection([('warning', 'Warning'), ('block', 'Block')],compute="_compute_credit_limit_type")

    @api.depends('credit_limit_type')
    def _compute_credit_limit_type(self):
        self.compute_credit_limit_type = False
        for rec in self:
            if rec.parent_id:
                rec.compute_credit_limit_type = rec.parent_id.credit_limit_type
            else:
                rec.compute_credit_limit_type = rec.credit_limit_type

    @api.depends('amount_credit_limit')
    @api.depends_context('company')
    def _compute_credit_limit_compute(self):
        print("\n\n\n11111111111\n\n\n")
        for partner in self:
            if partner.parent_id:
                print("\n\n\nwhy not gone\n\n\n",partner.parent_id.account_default_credit_limit)
                partner.credit_limit_compute = partner.parent_id.account_default_credit_limit if partner.parent_id.amount_credit_limit == -1 else partner.parent_id.amount_credit_limit    
            else:
                partner.credit_limit_compute = partner.account_default_credit_limit if partner.amount_credit_limit == -1 else partner.amount_credit_limit

    @api.depends('credit_limit_compute')
    @api.depends_context('company')
    def _inverse_credit_limit_compute(self):
        print("\n\n\n2222222222222\n\n\n")
        for partner in self:
            if partner.parent_id:
                is_default = partner.parent_id.credit_limit_compute == partner.parent_id.account_default_credit_limit
                partner.amount_credit_limit = -1 if is_default else partner.parent_id.credit_limit_compute
            else:
                is_default = partner.credit_limit_compute == partner.account_default_credit_limit
                partner.amount_credit_limit = -1 if is_default else partner.credit_limit_compute

    @api.depends_context('company')
    def _compute_show_credit_limit(self):
        print("\n\n\n3333333333333\n\n\n")
        for partner in self:
            if partner.parent_id:
                partner.show_credit_limit = partner.parent_id.account_credit_limit
            else:
                partner.show_credit_limit = partner.account_credit_limit

    def _commercial_fields(self):
        print("\n\n\n44444444\n\n\n")
        return super(ResPartner, self)._commercial_fields() + ['amount_credit_limit']
