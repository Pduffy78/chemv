import time
from odoo import api, models, _

class ReportBatchPayment(models.AbstractModel):

    _name = 'report.batch_payment.report_ap_batch_payment_pdf'

    def _get_partner(self,docs):
        partner_list = []
        for data in docs.vendor_bill_ids:
           partner_list.append(data.invoice_id.partner_id)
        return list(set(partner_list))
    
    
    
    def _get_partner_invoice_line(self,o,partner):
        invoice_lines = self.env['vendor.invoice.ap'].search([('invoice_id.partner_id', '=', partner.id),('vendor_id','=',o.id)])
        return invoice_lines
        
   
    def _get_total_pay_to_date(self,lines):
        pay_to_date = lines.invoice_id.amount_total - lines.invoice_id.amount_residual
        return pay_to_date
        
    
    def _get_total_amount_to_be_paid(self,lines):
#         pay_to_date = lines.invoice_id.amount_total - lines.invoice_id.residual
        amount_to_be_paid = lines.pay_amount
        return amount_to_be_paid
        
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
       
        docs = self.env['ix.batch.payment.ap'].browse(docids)
        return {
            'doc_ids': self.ids,
            'doc_model': 'ix.batch.payment.ap',
            'data': data,
            'docs': docs,
            'get_partner': self._get_partner,
            'get_partner_invoice_line': self._get_partner_invoice_line,
            'get_total_pay_to_date' : self._get_total_pay_to_date,
            'get_total_amount_to_be_paid' : self._get_total_amount_to_be_paid,
#            'get_partner_lines': movelines,
           
        }   