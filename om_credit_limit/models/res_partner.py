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



    @api.depends_context('company')
    def _credit_debit_get(self):
        tables, where_clause, where_params = self.env['account.move.line'].with_context(state='posted', company_id=self.env.company.id)._query_get()
        where_params = [tuple(self.ids)] + where_params
        if where_clause:
            where_clause = 'AND ' + where_clause
        print("tables:::::::::::::::::",tables)
        print("where_clause:::::::::::::::::",where_clause)
        print("where_params:::::::::::::::::",isinstance(self.id, int))
        if isinstance(self.id, int):
            self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
                          FROM """ + tables + """
                          LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                          LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                          WHERE act.type IN ('receivable','payable')
                          AND account_move_line.partner_id IN %s
                          AND account_move_line.reconciled IS NOT TRUE
                          """ + where_clause + """
                          GROUP BY account_move_line.partner_id, act.type
                          """, where_params)
            treated = self.browse()
            for pid, type, val in self._cr.fetchall():
                partner = self.browse(pid)
                if type == 'receivable':
                    partner.credit = val
                    if partner not in treated:
                        partner.debit = False
                        treated |= partner
                elif type == 'payable':
                    partner.debit = -val
                    if partner not in treated:
                        partner.credit = False
                        treated |= partner
            remaining = (self - treated)
            remaining.debit = False
            remaining.credit = False
        else:
            for rec in self:
                rec.debit = False
                rec.credit = False