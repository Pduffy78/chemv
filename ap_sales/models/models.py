# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ap_sales(models.Model):
    _inherit = 'sale.order'

    exchange_rate_date = fields.Date('Exchange Rate Date',default=fields.Date.context_today)
    exchange_rate = fields.Float('Exchange Rate')

class Currency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_rates(company, date)
        res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        print('_get_conversion_rate........',res,self._context)
        if self._context and self._context.get('active_model') and self._context.get('active_model') == 'sale.order' and self._context.get('active_id'):
            current_sale = self.env['sale.order'].browse([self._context.get('active_id')])
            if current_sale and current_sale.exchange_rate:
                res = 1 / current_sale.exchange_rate
        return res