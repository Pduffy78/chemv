from odoo import fields, models, api
from odoo.addons.payment import utils as payment_utils
import re
from werkzeug import urls
from odoo.addons.ap_ozow_payment_acquirer.controller.main import OzowController
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.ap_ozow_payment_acquirer.const import SUPPORTED_CURRENCIES
import requests
import json
import hashlib
import hmac
import base64



class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(
        selection_add=[('ozow_payment', 'Ozow Payment')],
        ondelete={'ozow_payment': 'set default'})

    ozow_site_code = fields.Char('OZOW Site Code',
                                      required_if_provider='ozow_payment')
    ozow_secret_key = fields.Char('OZOW Secret Key',
                                 required_if_provider='ozow_payment')
    ozow_api_key = fields.Char('OZOW API Key',
                                 required_if_provider='ozow_payment')


    def _get_ozow_urls(self, environment):
        """ payfast URLS """
        if environment == 'prod':
            return {
                'ozow_form_url':
                    ' https://api.ozow.com/PostPaymentRequest',
            }
        else:
            return {
                'ozow_form_url':
                    ' https://stagingapi.ozow.com/PostPaymentRequest',
            }
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
                lambda a: a.provider != 'ozow_payment')
        return acquirers

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'ozow_payment':
            return super()._get_default_payment_method_id()
        return self.env.ref(
            'ap_ozow_payment_acquirer.payment_method_ozow').id

    def yoco_get_form_action_url(self):
        return self._get_ozow_urls()['ozow_form_url']

    def _ozow_get_api_url(self):
        """ Get the form url of Yoco"""
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_ozow_urls(environment
                                      )['ozow_form_url']


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        checkout_id = ""
        if self.provider != 'ozow_payment':
            return res
        partner_first_name, partner_last_name = \
            payment_utils.split_partner_name(self.partner_name)
        base_url = self.acquirer_id.get_base_url()
        ozow_tx_values = dict(processing_values)
        ##### Prepare hash check #####
        amount = str(ozow_tx_values['amount'])
        if amount:
            if len(amount.split('.')[1]) == 1: 
                amount = str(amount)+'0'
            amt_temp = amount.split('.')
            amt_new = ''
            if len(amt_temp) > 1 and len(amt_temp[1]) > 2:
                amt_new = amt_temp[0] + '.' + amt_temp[1][0:2]
                amount = amt_new


        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #amount = str(ozow_tx_values['amount'])
        country_code = "ZA"
        currency_code = self.env["res.currency"].search([("id","=",ozow_tx_values["currency_id"])]).name 
        transaction_reference = ozow_tx_values['reference'] 
        bank_reference = ozow_tx_values['reference']
        cancel_url = base_url + '/payment/ozow/cancel/'
        error_url = base_url + '/payment/ozow/return/' 
        success_url= base_url + '/payment/ozow/success/'
        notify_url= base_url + '/payment/ozow/notify/'
        is_test = False
        
        input_string = str(self.acquirer_id.ozow_site_code) + str(country_code) + str(currency_code) + str(amount) + str(transaction_reference) + str(bank_reference) + str(cancel_url) + str(error_url) + str(success_url) + str(notify_url) + str(is_test) + str(self.acquirer_id.ozow_secret_key)
        checksum_hash = hashlib.sha512(input_string.encode('utf-8').lower()).hexdigest()
        #### header Authentication #####
        headers = {
        "Accept": "application/json",
	    "ApiKey": self.acquirer_id.ozow_api_key,
	    "Content-Type": "application/json"
        }

        data = {
            'siteCode': self.acquirer_id.ozow_site_code,
            'ozow_secret_key': self.acquirer_id.ozow_secret_key,
            'amount': amount,
            'currencyCode': "ZAR",
            "countryCode": "ZA",
            'hashCheck': checksum_hash,
            'cancelUrl': '%s' % urls.url_join
            (base_url, OzowController._cancel_url),
            'm_payment_id': processing_values['reference'],
            'item_name': processing_values['reference'],
            'transactionReference': processing_values['reference'],
            'bankReference': processing_values['reference'],
            'isTest': False,
            'email_address': self.partner_email,
            'name_first': partner_first_name,
            'name_last': partner_last_name,
            'custom_int1': re.sub("[^0-9]", "", self.partner_phone),
            'custom_str1': processing_values['reference'],
            'item_description':
                '%s:%s' % (
                    self.company_id.name, processing_values['reference']),
            'successUrl': '%s' % urls.url_join(
                base_url, OzowController._success_url),
            'notifyUrl': '%s' % urls.url_join
            (base_url, OzowController._notify_url),
            "errorUrl": '%s' % urls.url_join
            (base_url, OzowController._error_url)
        }
        api_url = self.acquirer_id._ozow_get_api_url()
        response = requests.post(api_url, headers=headers, json=data)
        response_data = response.json()
        print("response_data.............................................................",response_data)
        checkout_url = ""
        if response.status_code == 200:
            checkout_url = response_data['paymentRequestId']
            print("checkout_url//////////////////////////////////////////",checkout_url)
        else:
            print('Error creating charge token:')
            print(response_data)
            #checkout_id = response_data['id']

        print("checkout_url===================================",checkout_url)
        data['api_url'] = f"https://stagingpay.ozow.com/{checkout_url}/Secure"
        print("data['api_url']=====================================================",data['api_url'])
        ozow_tx_values.update(data)
        return ozow_tx_values

    def _get_tx_from_feedback_data(self, provider, data):
        """ Given a data dict coming from payfast, verify it and find '
        'the related transaction record."""
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'ozow_payment':
            return tx

        reference = data.get('m_payment_id')
        ref = data.get('reference')
        if not reference and not ref:
            error_msg = _(
                'Yoco Payment: received data with missing reference (%s)'
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
    
    def _process_feedback_data(self, data):
        """ Override of payment to process
        the transaction based on payfast data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'ozow_payment':
            return
        payment_status = data.get('payment_status')
        if data.get('payment_status') == 'COMPLETE':
            self._set_done()
        elif data.get('payment_status') == 'CANCEL':
            self._set_canceled()
        else:
            _logger.info(
                "Payment is %s",
                payment_status)
            self._set_error(
                "Yoco: " +
                _("Received data with invalid payment status: %s",
                  payment_status)
            )

