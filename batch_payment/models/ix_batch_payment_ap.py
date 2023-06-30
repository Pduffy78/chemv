# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import find_in_path
from odoo.tools import config
from odoo.sql_db import TestCursor
from odoo.http import request
import time
import base64
import io
import logging
import os
import lxml.html
import tempfile
import subprocess
import re
from lxml import etree
from io import StringIO, BytesIO
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

class ix_batch_payment_ap(models.Model):
    _name='ix.batch.payment.ap'
    _rec_name = 'payment_date'

    def default_vendor_bills(self):
        if self._context and self._context.get('uid'):
            # user_id = self.env['res.users'].browse(self._context.get('uid'))
            invoices = self.env['account.move'].browse(self._context.get('active_ids'))
            # invoices = self.env['account.move'].search([('partner_id' , '=' ,1)])
            rec_list = []
            for data in invoices:
                # if data.state not in ['draft']:
                if data.state not in ['posted']:
                    raise UserError(_('You can only register payments for open invoices'))
                if not data.partner_id.is_approve:
                    raise UserError(_('Please approve bank details of %s')%data.partner_id.name)
                ap_tuple = (0,0,{
                    'invoice_id' : data.id,
                    'partner_id' : data.partner_id.id,
                    'number' : data.number,
                    'balance_amount' : data.amount_total,
                    'pay_amount' : data.amount_residual_signed,
                     'amount_untaxed' : data.amount_untaxed,
                    })
                rec_list.append(ap_tuple)
            return rec_list
        
    @api.onchange('invoice_ids')
    def onchange_invoice_ids(self):
        if self.invoice_ids:
            rec_list = []
            for data in self.invoice_ids:
                if data in self.invoice_list_ids:
                    continue
                # if data.state not in ['draft']:
                if data.state not in ['posted']:
                    raise UserError(_('You can only register payments for open invoices'))
                if not data.partner_id.is_approve:
                    raise UserError(_('Please approve bank details of %s')%data.partner_id.name)
                ap_tuple = (0,0,{
                    'invoice_id' : data.id,
                    'partner_id' : data.partner_id.id,
                    'number' : data.number,
                    'balance_amount' : data.amount_total,
                    'pay_amount' : data.amount_residual_signed,
                    'amount_untaxed' : data.amount_untaxed,
                    })
                rec_list.append(ap_tuple)
            self.vendor_bill_ids = rec_list
        
    # @api.multi
    def print_batch_payment_vendor(self):
        return {
                 'name': 'test',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ix.batch.payment.vendor.report',
                'view_id': self.env.ref('batch_payment.view_batch_payment_xls_report_vendor').id or False,
                'type': 'ir.actions.act_window',
                'target': 'new'
               }   

    # @api.one
    def save_rec(self):
        for lines in self.vendor_bill_ids:
            if not lines.pay_amount:
                raise UserError(_('Please fill Pay Amount'))
        self.ensure_one()
        
    def default_company_id(self):
        if self._context.get('active_ids'):
            vendor_bills = self.env['account.move'].browse(self._context.get('active_ids'))
            if len(vendor_bills.mapped('company_id')) > 1:
                raise UserError(_('Please select Vendor bills of only one Company'))
            return vendor_bills.mapped('company_id')
        else:
            return self.env.user.company_id.id
        
    def default_bank_id(self):
        if self._context.get('active_ids'):
            vendor_bills = self.env['account.move'].browse(self._context.get('active_ids'))
            return self.env['account.journal'].search([('name','=','Standard Bank - Current'),('company_id','=',vendor_bills.mapped('company_id').id)]).id
        else:
            return self.env['account.journal'].search([('name','=','Standard Bank - Current'),('company_id','=',self.env.user.company_id.id)]).id
    
    state = fields.Selection([('to be approved','To Be Approved'),('approved','Approved'),('rejected','Rejected')], string="State", default="to be approved")
    payment_date = fields.Date(string="Payment Date")
    memo = fields.Char(string="Memo")
    vendor_bill_ids = fields.One2many('vendor.invoice.ap','vendor_id',string='Vendor bill',default=default_vendor_bills)
    requested_person_id = fields.Many2one('res.users',string="Requested Person")
    approve_person_id = fields.Many2one('res.users',string="Approved Person")
    run_date = fields.Date(string='Run Date')
    number = fields.Char('Number')
    company_id = fields.Many2one('res.company',default=default_company_id)
    bank_id = fields.Many2one('account.journal',string="Bank",default=default_bank_id)
    invoice_ids = fields.Many2many('account.move')
    invoice_list_ids = fields.Many2many('account.move',compute="compute_invoice_list_ids")
    is_add = fields.Boolean(default=False,string="Add More Vendor Bills")
    
    # @api.one
    @api.depends('vendor_bill_ids')
    def compute_invoice_list_ids(self):
        invoices = [ data.id for data in self.vendor_bill_ids.mapped('invoice_id')]
        self.invoice_list_ids = [(6,0,invoices)]
    
    # @api.multi
    def btn_approved(self):
        if self.vendor_bill_ids.filtered(lambda x: x.invoice_id.state == 'paid'):
            raise UserError(_('Vendor bill %s is already been paid')%self.vendor_bill_ids.filtered(lambda x: x.invoice_id.state in ['paid', 'in_payment'])[0].invoice_id.number)
        partners = self.vendor_bill_ids.mapped('partner_id')
        for partner in partners:
            invoice_ids = []
            invoice_rec_ids = []
            total_amount = 0.00
            communication = ""
            payment_type =""
            partner_type =""
            payment_methods=""
            for line in self.vendor_bill_ids.filtered(lambda x: x.partner_id == partner  and x.invoice_id.state == 'posted' and x.invoice_id.payment_state not in ['paid', 'in_payment']):
                if not line.partner_id.is_approve:
                    raise UserError(_('Please approve bank details of %s')%line.partner_id.name)
                if not self.bank_id:
                    raise UserError(_('Please select a bank.'))
                print(line.invoice_id)
                if line.invoice_id.state == 'posted' and line.invoice_id.payment_state not in ['paid', 'in_payment']:
                    # if line.invoice_id.state == 'posted':
                    print
                    if line.invoice_id.move_type == 'in_invoice':
                        payment_type = 'outbound'
                        partner_type = 'supplier'
                    elif line.invoice_id.move_type == 'out_invoice':
                        payment_type = 'inbound'
                        partner_type = 'customer'
                    # payment_methods = self.bank_id.outbound_payment_method_ids
                    payment_methods = self.bank_id.available_payment_method_ids
                    invoice_ids.append(line.invoice_id.id)
                    invoice_rec_ids.append(line.invoice_id)
                    line_pay_amount = line.pay_amount
                    if line.pay_amount < 0:
                        line_pay_amount = -1 * line_pay_amount
                    total_amount += line_pay_amount
                    communication += str(line.invoice_id.number) + " "
            if invoice_ids :
                invoice_ids =  [(6,0,invoice_ids)] 
            else:
                invoice_ids = []

            vals = {'partner_type': partner_type,
                    'payment_type': payment_type, 
                    'partner_id': partner and partner.id, 
                    'amount':  total_amount, 
                    'date': self.payment_date, 
                    'ref': communication,
                    'journal_id': self.bank_id.id
                    }
            payment = self.env['account.payment'].create(vals)
            payment.action_post()
            payment_move_line_debit = payment.move_id.line_ids.filtered(lambda x: x.debit and x.debit not in [0, 0.0, 0.00])
            payment_move_line_credit = payment.move_id.line_ids.filtered(lambda x: x.credit and x.credit not in [0, 0.0, 0.00])
            for inv in invoice_rec_ids:
                inv.js_assign_outstanding_line(payment_move_line_debit.ids)
                inv.js_assign_outstanding_line(payment_move_line_credit.ids)
        self.state ='approved'
    
    # @api.one
    def btn_rejected(self):
        self.state ='rejected'  
        
    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.vendor_bill_ids:
                raise UserError(_('You do not have access to delete batch payments.'))
        return super(batch_payment_ap, self).unlink()
    
    # @api.multi
    def print_batch_payment_pdf(self):
        return self.env.ref('batch_payment.action_ap_batch_payment').report_action(self)

    @api.model
    def create(self, vals):
        result = super(ix_batch_payment_ap, self).create(vals)
        if result and vals.get('payment_date'):
            split_date = vals.get('payment_date').split('-')
            date_res = ''.join(map(str, split_date))
            new_seq = self.env['ir.sequence'].with_context(force_company=result.company_id.id).next_by_code("ix.batch.payment.ap")
            if new_seq:
                sequence = 'SB' + date_res + 'EFT' + new_seq
                result.write({'number': sequence})
        return result
    
    # @api.multi
    def write(self, vals):
        result = super(ix_batch_payment_ap, self).write(vals)
        for rec in self.filtered(lambda x: x.invoice_ids):
            rec.invoice_ids = False
            rec.is_add = False
        return result

    # @api.multi
    def print_batch_payment_csv(self):
        """Batch Payment report in (XLS)."""
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
        j = 0
        ws.append( wb.add_worksheet() )
        ws[j].set_column('A:A', 20.25)
        ws[j].set_column('B:B', 20.25)
        ws[j].set_column('C:C', 20.25)
        ws[j].set_column('D:Z', 15.25)
        i = 1
        ws[j].write(0, 0, 'Cr Account Name', style1)
        ws[j].write(0, 1, 'Cr Account Number', style1)  
        ws[j].write(0, 2, 'Cr Branch Number', style1)
        ws[j].write(0, 3, 'Cr Statement Reference', style1)    
        ws[j].write(0, 4, 'Dr Account Name', style1)  
        ws[j].write(0, 5, 'Dr Account Number', style1) 
        ws[j].write(0, 6, 'Dr Branch Number', style1) 
        ws[j].write(0, 7, 'Dr Statement Reference', style1) 
        ws[j].write(0, 8, 'Date', style1) 
        ws[j].write(0, 9, 'Amount', style1)
        ws[j].write(0, 10, 'RTGS/RTC', style1)
        ws[j].write(0, 11, 'Pay Alert Type', style1) 
        ws[j].write(0, 12, 'Pay Alert Destination', style1) 
        cnt = 0
        partners = set(self.vendor_bill_ids.mapped('partner_id'))
        for partner in partners:
            for line in self.vendor_bill_ids.filtered(lambda x: x.partner_id == partner):
                record = line
                cnt = cnt + 1
                ws[j].write(i, 0, record.partner_id.name[:30], style0)
                ws[j].write(i, 1, record.partner_id.acc_no_ap, style0)
                ws[j].write(i, 2, record.partner_id.branch_name_code, style0)
                ws[j].write(i, 3, self.env.user.company_id.name, style0)
                ws[j].write(i, 4, self.env.user.company_id.name, style0)
                ws[j].write(i, 5, self.company_id.dr_account_number, style0)
                ws[j].write(i, 6, self.company_id.dr_branch_number, style0)
                ws[j].write(i, 7, self.number, style0)
                ws[j].write(i, 8, str(self.payment_date).replace("-",""), style0)
                ws[j].write(i, 9, sum(self.vendor_bill_ids.filtered(lambda x: x.partner_id == partner).mapped('pay_amount')), style0)
                ws[j].write(i, 10, 'N', style0)
                ws[j].write(i, 11, 'E', style0)
                ws[j].write(i, 12, record.partner_id.email, style0)
            i += 1

        wb.close()
        fl.seek(0)
        buf = base64.encodebytes(fl.read())
        fl.flush()
        fl.close()

        a1 = self.env['batch.payment.csv.wizrd'].create({
                'file': buf,
                'file_name': 'Batch_Payment.xls',
                'exported': True
                }
            )
        return {
            'name': _('Batch Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batch.payment.csv.wizrd',
            'view_id': False,
            'res_id': a1.id,
            'type': 'ir.actions.act_window',
            'context': {},
            'target': 'new',
        }
class vendor_invoice_ap(models.Model):
    _name='vendor.invoice.ap' 
   
    vendor_id = fields.Many2one('ix.batch.payment.ap',string='Vendor')
    invoice_id = fields.Many2one('account.move',string='Supplier Invoice')
    partner_id = fields.Many2one('res.partner',string="Supplier")
    number = fields.Char(string="Supplier Invoice")
    balance_amount = fields.Float(string='Balance Amount')
    pay_amount = fields.Float(string='Pay Amount')
    amount_untaxed = fields.Float(string="Untaxed Amount")

class inheritrespartner(models.Model):
    _inherit = 'res.partner'

    bank_financial_inst = fields.Char(string='Bank / Financial institution:',track_visibility="onchange")
    branch_name_code = fields.Char(string='Branch name and code:',track_visibility="onchange")
    acc_no_ap = fields.Char(string='Bank account number:',track_visibility="onchange")
    type_account = fields.Char( string='Type of account:',track_visibility="onchange")
    swift_code = fields.Char(string='Swift Code:',track_visibility="onchange")
    tel_ph_dtls = fields.Char( string='Telephone details (accounts department contact person)',track_visibility="onchange")

    is_approve = fields.Boolean(string="Is approved")

    def button_approve(self):
        msg = "Banking Details has been approved by  %s on %s" % (self.env.user.name, str(datetime.now().date()))
        self.message_post(body=msg)
        self.is_approve = True

class AccountInvoice(models.Model):
    _inherit = "account.move"

    proman_inv = fields.Char(string="Proman Inv. No")
    is_generate_vat_by_subtotal = fields.Boolean(default=False,string="Generate the VAT by Invoice line")
    number = fields.Char('Number')

    @api.model
    def invoice_line_move_line_get(self):#Overriden to add project and task to the account.move.line when customer invoice is validated.
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for data in res:
            invoice_line = self.env['account.move.line'].browse(data.get('invl_id'))
            data.update({'project_id':self.project_id and self.project_id.id,
                         'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id,
                         'task_id': invoice_line.task_id and invoice_line.task_id.id,
                         #'analytic_line_ids': [(6,0,invoice_line.analytic_line_ids.ids)] 
                         })
        return res

    @api.model
    def _get_group_info(self):
        res = False
        user = self.env['res.users'].browse(self._context.get('uid'))
        pm_approval = user.user_has_groups('ix_batch_payment_ap.group_force_pm_approval')
        if pm_approval:
            res = True
        for rec in self:
            rec.is_pm_validated = res

    is_pm_validated = fields.Boolean('Is PM Validated', compute='_get_group_info')
    pm_validated = fields.Float('Total Varification', track_visibility='onchange')
    wp_invoice_number = fields.Char('WP Invoice Number', track_visibility='onchange')

    # @api.multi
    def action_pm_validate(self):
        self.ensure_one()
        if self.project_id and self.project_id.user_id and self.project_id.user_id.id != self._context.get('uid', False):
            raise ValidationError(_('Only project manager can Validate.'))
        self.message_post(body="PM Validated : %s" %(self.pm_validated),
                          subject="PM validated")
        return self.write({'is_pm_validated': True})
    
    
    @api.model
    def cron_tags(self):
        for data in self.env['account.move'].search([('project_id','!=',False)]):
           for line in data.invoice_line_ids:
               if not line.analytic_tag_ids:
                   line.analytic_tag_ids = data.project_id.branch_ids + data.project_id.department_ids
        for journal in self.env['account.move.line'].search(['|',('project_id','!=',False),('analytic_account_id','!=',False)]):
            if not journal.analytic_tag_ids:
                project_id = journal.project_id
                if not project_id:
                    project_id = journal.analytic_account_id.project_id
                journal.analytic_tag_ids = project_id.branch_ids + project_id.department_ids
     
    def unlink(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                for data in line.analytic_line_ids:
                    data.write({'is_invoiced' : False,'invoice_status': 'toinvoice', 'amount_invoiced': 0,
                                    'quantity_invoiced': 0 })
        return super(AccountInvoice, self).unlink()
    
    
class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    is_batch_payment = fields.Boolean(string='Is Batch Payment',default=False)
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    dr_account_number = fields.Char(string='Dr Account Number')
    dr_branch_number = fields.Char(string='Dr Branch Number')
    
    
    
    
    