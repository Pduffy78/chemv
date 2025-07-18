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
        print("post=========",post)
        reference = post.get('m_payment_id') or post.get('reference')
        if reference:
            _logger.info('PayFast: validated data')
            res = request.env['payment.transaction'].sudo()._get_velidate_data(post)
            return res

    @http.route([
        '/payment/payfast/notify',
    ], type='http', auth='public', csrf=False)
    def payfast_notify(self, **post):
        """ Gets the Post data of payfast after making payment """
        _logger.info('PayFast: entering form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', post.get('m_payment_id'))])
        if tx:
            tx.write({
                'reference': post.get('pf_payment_id')
            })
        # return True

    @http.route([
        '/payment/payfast/return',
    ], type='http', auth='public', website=True,
        csrf=False)
    def payfast_return(self, **post):
        _logger.info('PayFast: returning with post data %s',
                     pprint.pformat(post))
        order = request.session.get('sale_last_order_id')
        print("post===========",post,request.context,request.session)
        for key,value in request.session.items():
            print("key========",key,value)
        if not post:
            if order:
                sale_order = request.env['sale.order'].\
                    sudo().search([('id', '=', order)])
                post['reference'] = sale_order.name
                post['payment_status'] = 'COMPLETE'
                post['transaction_id'] = request.session.get('__website_sale_last_tx_id')
                
                request.env['payment.transaction'].\
                    sudo()._get_velidate_data(post)
        return request.redirect('/payment/status')

    @http.route([
        '/payment/payfast/cancel'
    ], type='http', auth='public', website=True,
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
                post['transaction_id'] = request.session.get('__website_sale_last_tx_id')
                self.payfast_validate_data(**post)
        return werkzeug.utils.redirect('/payment/status')