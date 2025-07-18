# -*- coding: utf-8 -*-
import logging
import datetime
from math import copysign

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.tools import config, date_utils, get_lang
from odoo.tools.misc import formatLang, format_date
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountReportExtended(models.AbstractModel):
    _inherit = 'account.report'

    filter_account = True

    @api.model
    def _get_filter_account(self):
       
        return self.env['res.users'].search([])

    @api.model
    def _init_options_account(self, options, previous_options=None):
        if self.filter_account is None:
            return

        previous_company = False
        if previous_options and previous_options.get('account'):
            journal_map = dict((opt['id'], opt['selected']) for opt in previous_options['account'] if opt['id'] != 'divider' and 'selected' in opt)
        else:
            journal_map = {}
        options['account'] = []
        
        for op in self._get_filter_account():
            options['account'].append({
                'id': op.id,
                'account_id': op.id,
                'account_name': op.name,
                'selected': journal_map.get(op.id) or False,
            })

    @api.model
    def _get_options_account(self, options):
        return [
            account for account in options.get('account', []) if account['selected']
        ]

    @api.model
    def _get_options_account_domain(self, options):
        # Make sure to return an empty array when nothing selected to handle archived journals.
        selected_account = self._get_options_account(options)
        return selected_account and [('move_id.invoice_user_id', 'in', [j['id'] for j in selected_account])] or []

    @api.model
    def _get_options_domain(self, options,data_scope):
        res = super(AccountReportExtended, self)._get_options_domain(options,data_scope)
        res += self._get_options_account_domain(options)
        return res


    
    
    
    
    
    
    