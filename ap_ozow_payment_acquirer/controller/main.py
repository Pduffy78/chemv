import logging
import pprint
import werkzeug
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OzowController(http.Controller):
    """ Handles the redirection back from payment gateway to merchant site """

    _notify_url = '/payment/ozow/notify/'
    _cancel_url = '/payment/ozow/cancel/'
    _success_url = '/payment/ozow/success/'
    _error_url = '/payment/ozow/return/'

    def ozow_validate_data(self, **post):
        """ Validate the data coming from Ozow payment. """
        res = False
        reference = post.get('m_payment_id') or post.get('reference')
        if reference:
            _logger.info('YocoPayment: validated data')
            res = request.env['payment.transaction'].sudo().\
                _handle_feedback_data(
                'ozow_payment', post)
            return res
    
    @http.route([
        '/payment/ozow/success',
    ], type='http', auth='user', website=True,
        csrf=False)
    def ozow_return(self, **post):
        _logger.info('Ozow: returning with post data %s',
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
                    'ozow_payment', post)
        return request.redirect('/payment/status')

    @http.route([
        '/payment/ozow/cancel/'
    ], type='http', auth='user', website=True,
        csrf=False)
    def ozow_cancel(self, **post):
        _logger.info('Ozow: cancel with post data %s',
                     pprint.pformat(post))
        order = request.session.get('sale_last_order_id')
        if not post.get('pf_payment_id'):
            if order:
                sale_order = request.env['sale.order'].\
                    sudo().search([('id', '=', order)])
                post['reference'] = sale_order.name
                post['payment_status'] = 'CANCEL'
                self.ozow_validate_data(**post)
        return werkzeug.utils.redirect('/payment/status')
