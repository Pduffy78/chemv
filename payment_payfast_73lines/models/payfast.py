# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

""" This file manages all the operations and the functionality of the gateway
integration """

import logging
import re
from hashlib import md5
import urllib
import urllib.parse
from werkzeug import urls
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo import fields, models, api
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_payfast_73lines.const import SUPPORTED_CURRENCIES
from odoo.addons.payment_payfast_73lines.controllers.main import \
    PayFastController
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['payfast_73lines'] = \
            {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res


class AcquirerPayFast(models.Model):
    """ Class to handle all the functions required in integration """
    _inherit = 'payment.provider'

    def _get_payfast_urls(self, environment):
        """ payfast URLS """
        if environment == 'prod':
            return {
                'payfast_form_url':
                    'https://www.payfast.co.za/eng/process',
            }
        else:
            return {
                'payfast_form_url':
                    'https://sandbox.payfast.co.za/eng/process',
            }

    code = fields.Selection(
        selection_add=[('payfast_73lines', 'PayFast')],
        ondelete={'payfast_73lines': 'set default'})
    payfast_merchant_id = fields.Char('PayFast Merchant Id',
                                      required_if_code='payfast_73lines')
    payfast_secret = fields.Char('PayFast Secret Key',
                                 required_if_code='payfast_73lines')
    payfast_passphrase = fields.Char('PayFast Passphrase Key')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Mollie
         acquirers for unsupported currencies. """
        acquirers = \
            super()._get_compatible_acquirers(
                *args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in SUPPORTED_CURRENCIES:
            acquirers = acquirers.filtered(
                lambda a: a.code != 'payfast_73lines')
        return acquirers

    def _get_default_payment_method_id(self,code):
        self.ensure_one()
        if self.code != 'payfast_73lines':
            return super()._get_default_payment_method_id(self.code)
        return self.env.ref(
            'payment_payfast_73lines.payment_method_payfast').id

    def _payfast_generate_auth(self, data):
        """ Generate the md5 hash used in making payment in payfast"""
        output = ''
        new_dict = {}
        for key in data:
            val = str(data[key]).replace(' ', '+')
            new_dict[key] = urllib.parse.quote(val, safe='')
        output = 'merchant_id=' + new_dict['merchant_id'] + '&' + \
                 'merchant_key=' + new_dict['merchant_key'] + '&' + \
                 'return_url=' \
                 + new_dict['return_url'] + '&' + 'cancel_url=' + \
                 new_dict['cancel_url'] + '&' + 'notify_url=' + \
                 new_dict['notify_url'] + '&' + 'name_first=' + \
                 new_dict['name_first'] + '&' + 'name_last=' + \
                 new_dict['name_last'] + '&' + 'email_address=' + \
                 new_dict['email_address'] + '&' + 'm_payment_id=' + \
                 new_dict['m_payment_id'] \
                 + '&' + 'amount=' + new_dict['amount'] + \
                 '&' + 'item_name=' + new_dict['item_name'] + '&' + \
                 'item_description=' + new_dict['item_description'] + '&' + \
                 'custom_int1=' \
                 + new_dict['custom_int1'] + '&' + 'custom_str1=' + \
                 new_dict['custom_str1']
        if self.payfast_passphrase:
            output = output + '&passphrase=' + str(self.payfast_passphrase)
        signature = md5(output.encode('utf-8')).hexdigest()
        return signature

    def _payfast_get_api_url(self):
        """ Get the form url of payfast"""
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_payfast_urls(environment
                                      )['payfast_form_url']


class TxPayFast73lines(models.Model):
    """ Handles the functions for validation after transaction is processed """
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'payfast_73lines':
            return res
        partner_first_name, partner_last_name = \
            payment_utils.split_partner_name(self.partner_name)
        base_url = self.provider_id.get_base_url()
        payfast_tx_values = dict(processing_values)
        data = {
            'merchant_id': self.provider_id.payfast_merchant_id,
            'merchant_key': self.provider_id.payfast_secret,
            'amount': processing_values['amount'],
            'm_payment_id': processing_values['reference'],
            'item_name': processing_values['reference'],
            'email_address': self.partner_email,
            'name_first': partner_first_name,
            'name_last': partner_last_name,
            'custom_int1': re.sub("[^0-9]", "", self.partner_phone),
            'custom_str1': processing_values['reference'],
            'item_description':
                '%s:%s' % (
                    self.company_id.name, processing_values['reference']),
            'return_url': '%s' % urls.url_join(
                base_url, PayFastController._return_url),
            'notify_url': '%s' % urls.url_join
            (base_url, PayFastController._notify_url),
            'cancel_url': '%s' % urls.url_join
            (base_url, PayFastController._cancel_url),
            'api_url': self.provider_id._payfast_get_api_url(),
        }
        data['signature'] = self.provider_id._payfast_generate_auth(data)
        payfast_tx_values.update(data)
        return payfast_tx_values

    def _get_tx_from_feedback_data(self, provider, data):
        """ Given a data dict coming from payfast, verify it and find '
        'the related transaction record."""
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'payfast_73lines':
            return tx

        reference = data.get('m_payment_id')
        ref = data.get('reference')
        if not reference and not ref:
            error_msg = _(
                'PayFast: received data with missing reference (%s)'
            ) % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        if ref:
            tx_list = []
            for tx in self.search([]):
                tx_id = tx.reference.split('-')[0]
                if tx_id == ref:
                    tx_list.append(tx)
            if tx_list != 0:
                tx = tx_list[0]
            return tx

    def _get_velidate_data(self, data):
        print("self========================",self)
        transaction_id = self.env['payment.transaction'].search([('id','=',data.get('transaction_id'))])
        """ Override of payment to process
        the transaction based on payfast data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        


        if transaction_id.provider_id.code != 'payfast_73lines':
            return
        payment_status = data.get('payment_status')
        if data.get('payment_status') == 'COMPLETE':
            transaction_id._set_done()
        elif data.get('payment_status') == 'CANCEL':
            transaction_id._set_canceled()
        else:
            _logger.info(
                "Payment is %s",
                payment_status)
            transaction_id._set_error(
                "Payfast: " +
                _("Received data with invalid payment status: %s",
                  payment_status)
            )
