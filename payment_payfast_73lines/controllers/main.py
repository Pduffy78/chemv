# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

""" File to manage the functions used while redirection"""
import logging
import pprint
import werkzeug
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PayFastController(http.Controller):
    """ Handles the redirection back from payment gateway to merchant site """

    _notify_url = '/payment/payfast/notify'
    _cancel_url = '/payment/payfast/cancel/'
    _return_url = '/payment/payfast/return/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from payfast. """
        return_url = '/payment/process'
        return return_url

    def payfast_validate_data(self, **post):
        """ Validate the data coming from payfast. """
        res = False
        reference = post.get('m_payment_id') or post.get('reference')
        if reference:
            _logger.info('PayFast: validated data')
            res = request.env['payment.transaction'].sudo().\
                _handle_feedback_data(
                'payfast_73lines', post)
            return res

    @http.route([
        '/payment/payfast/notify',
    ], type='http', auth='none', csrf=False)
    def payfast_notify(self, **post):
        """ Gets the Post data of payfast after making payment """
        _logger.info('PayFast: entering form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', post.get('m_payment_id'))])
        if tx:
            tx.write({
                'acquirer_reference': post.get('pf_payment_id')
            })
        # return True

    @http.route([
        '/payment/payfast/return',
    ], type='http', auth='user', website=True,
        csrf=False)
    def payfast_return(self, **post):
        _logger.info('PayFast: returning with post data %s',
                     pprint.pformat(post))
        order = request.session.get('sale_last_order_id')
        if not post:
            if order:
                sale_order = request.env['sale.order'].\
                    sudo().search([('id', '=', order)])
                post['reference'] = sale_order.name
                post['payment_status'] = 'COMPLETE'
                request.env['payment.transaction'].\
                    sudo()._handle_feedback_data(
                    'payfast_73lines', post)
        return request.redirect('/payment/status')

    @http.route([
        '/payment/payfast/cancel'
    ], type='http', auth='user', website=True,
        csrf=False)
    def payfast_cancel(self, **post):
        _logger.info('PayFast: cancel with post data %s',
                     pprint.pformat(post))
        order = request.session.get('sale_last_order_id')
        if not post.get('pf_payment_id'):
            if order:
                sale_order = request.env['sale.order'].\
                    sudo().search([('id', '=', order)])
                post['reference'] = sale_order.name
                post['payment_status'] = 'CANCEL'
                self.payfast_validate_data(**post)
        return werkzeug.utils.redirect('/payment/status')
