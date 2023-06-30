from odoo import models, fields, api, _
import xlsxwriter   #import xlwt #help http://nullege.com/codes/search/xlwt.Style.easyxf    http://nullege.com/codes/search/xlwt
from io import StringIO
from io import BytesIO
import base64
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class batch_payment_csv_wizrd(models.TransientModel):
    _name = 'batch.payment.csv.wizrd'

    exported = fields.Boolean(string="Exported", default=False)
    file = fields.Binary(string="File")
    file_name = fields.Char(string="File Name", size=64, default='Batch Payment.xlsx')


class ix_batch_payment_vendor_report(models.TransientModel):
    _name = 'ix.batch.payment.vendor.report'
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')  
    file = fields.Binary(string="File")
    file_name = fields.Char(string="File Name", size=64, default='Batch Payment.xls')
    exported = fields.Boolean(string="Exported", default=False)


    # @api.multi
    def print_batch_payment_vendor_wizard(self):
        fl = BytesIO()
        fl.flush()
        wb = xlsxwriter.Workbook(fl)
        stylei = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'italic': True, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style0 = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style1 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style3 = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'num_format': '####0;-####0;"-"'})
        style5 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'top': 1, 'bottom': 2, 'num_format': '####0;-####0;"-"'})
        style4 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'top': 1, 'bottom': 2,                                'num_format': '#,##0.00;-#,##0.00;"-"'})
        style_percent = wb.add_format({'num_format': '0.00%'})
        ws = []
# #        --------header code----------
# 
        j = 0
        i = 1
        batch_payments = self.env['ix.batch.payment.ap'].search([('payment_date','>=',self.start_date),('payment_date','<=',self.end_date)])
        
        ws.append( wb.add_worksheet('Consolidated Summary') )
        for data in batch_payments:
            ws[j].set_column('A:A', 20.25)
            ws[j].set_column('B:B', 20.25)
            ws[j].set_column('C:C', 20.25)
            ws[j].set_column('D:Z', 15.25)
           
            ws[j].write(0, 0, 'Batch Date', style1)
            ws[j].write(0, 1, 'Supplier', style1)  
            ws[j].write(0, 2, 'Invoice Number', style1)
            ws[j].write(0, 3, 'Invoice Date', style1)    
            ws[j].write(0, 4, 'Transaction Reference', style1)  
            ws[j].write(0, 5, 'Transaction Description', style1) 
            ws[j].write(0, 6, 'Transaction Amount', style1) 
            ws[j].write(0, 7, 'Approved Amount', style1) 
            ws[j].write(0, 8, 'Paid to Date', style1) 
            ws[j].write(0, 9, 'Discount Recieved', style1)
            ws[j].write(0, 10, 'Amount to be Paid', style1)
            ws[j].write(0, 11, 'Branch', style1) 
            ws[j].write(0, 12, 'Account Number', style1) 
            ws[j].write(0, 13, 'Bank', style1) 
            ws[j].write(0, 14, 'Run Date', style1) 
            
            for lines in data.vendor_bill_ids:
                ws[j].write(i, 0, data.create_date, style0)
                ws[j].write(i, 1, lines.partner_id.name, style0)
                ws[j].write(i, 2, lines.invoice_id.number, style0)
                ws[j].write(i, 3, lines.invoice_id.invoice_date, style0)
                ws[j].write(i, 4, data.memo, style0)
                ws[j].write(i, 5, 'Vendor Payment', style0)
                ws[j].write(i, 6, lines.invoice_id.amount_total, style0)
                ws[j].write(i, 7, lines.pay_amount, style0)
                ws[j].write(i, 8, data.payment_date, style0)
                ws[j].write(i, 10, lines.pay_amount, style0)
                ws[j].write(i, 11, lines.partner_id.branch_name_code, style0)
                ws[j].write(i, 12, lines.partner_id.acc_no_ap, style0)
                ws[j].write(i, 13, lines.partner_id.bank_financial_inst, style0)
                ws[j].write(i, 14, data.run_date, style0)
                i += 1
            
        j = 1
        
        for data in batch_payments:
            ws.append( wb.add_worksheet() )
            ws[j].set_column('A:A', 20.25)
            ws[j].set_column('B:B', 20.25)
            ws[j].set_column('C:C', 20.25)
            ws[j].set_column('D:Z', 15.25)
            i = 2
           
            ws[j].write(0, 0, 'Batch Date', style1)
            ws[j].write(0, 1, 'Supplier', style1)  
            ws[j].write(0, 2, 'Invoice Number', style1)
            ws[j].write(0, 3, 'Invoice Date', style1)    
            ws[j].write(0, 4, 'Transaction Reference', style1)  
            ws[j].write(0, 5, 'Transaction Description', style1) 
            ws[j].write(0, 6, 'Transaction Amount', style1) 
            ws[j].write(0, 7, 'Approved Amount', style1) 
            ws[j].write(0, 8, 'Paid to Date', style1) 
            ws[j].write(0, 9, 'Discount Recieved', style1)
            ws[j].write(0, 10, 'Amount to be Paid', style1)
            ws[j].write(0, 11, 'Branch', style1) 
            ws[j].write(0, 12, 'Account Number', style1) 
            ws[j].write(0, 13, 'Bank', style1) 
            ws[j].write(0, 14, 'Run Date', style1) 
        
            
            total_approved = 0.0
            total_amount_total = 0.0
            for record in self.env['vendor.invoice.ap'].search([('vendor_id','=', data.id)]):
                total_approved += record.pay_amount
                total_amount_total += record.invoice_id.amount_total
                ws[j].write(i, 0, data.create_date, style0)
                ws[j].write(i, 1, record.partner_id.name, style0)
                ws[j].write(i, 2, record.invoice_id.number, style0)
                ws[j].write(i, 3, record.invoice_id.invoice_date, style0)
                ws[j].write(i, 4, data.memo, style0)
                ws[j].write(i, 5, 'Vendor Payment', style0)
                ws[j].write(i, 6, record.invoice_id.amount_total, style0)
                ws[j].write(i, 7, record.pay_amount, style0)
                ws[j].write(i, 8, data.payment_date, style0)
                ws[j].write(i, 10, record.pay_amount, style0)
                ws[j].write(i, 11, record.partner_id.branch_name_code, style0)
                ws[j].write(i, 12, record.partner_id.acc_no_ap, style0)
                ws[j].write(i, 13, record.partner_id.bank_financial_inst, style0)
                ws[j].write(i, 14, data.run_date, style0)
                i += 1
            
            ws[j].write(i, 0, 'Total', style1)  
            ws[j].write(i, 6, total_amount_total, style1)
            ws[j].write(i, 7, total_approved, style1)
            ws[j].write(i, 10, total_approved, style1)
            i += 2
            j += 1
         
        wb.close()
        fl.seek(0)
        buf = base64.encodebytes(fl.read())
        fl.flush()
        fl.close()
        self.file = buf
        self.exported = True
        return {
            'name':_("Batch Payment XLS"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'ix.batch.payment.vendor.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id
        }
        