from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from odoo.tools import  DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import xlsxwriter 
import base64
from io import StringIO
from io import BytesIO
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import io
import csv
import re
import string
    

class wizard_import_ap(models.TransientModel):
    _name = 'wizard.import.ap'
    
    upload_csv = fields.Binary(string="Upload csv file")
    ap_company_id = fields.Many2one("res.company", string = "Company")
    
    
    
    def duplicate_journals(self):
        print()
        

    def duplicate_accounts(self):
        account_obj = self.env['account.account']
        for account in account_obj.search([('company_id', '=', self.env.user.company_id.id)]):
            print('________',self.env.user.company_id.name)
            for company in self.env['res.company'].search([('id', '!=', self.env.user.company_id.id)]):
                if not account_obj.sudo().search([('company_id', '=', company.id),('code', '=', account.code)]):
                    print(account.code,'_________',company.name)
                    kk = account.with_company(company).copy(default={'company_id': company.id})
                    print(kk)
    
    
    def wizard_import(self):
        csv_data = base64.b64decode(self.upload_csv)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=',')
        file_reader.extend(csv_reader)
        partner_obj = self.env['res.partner']
        account_obj = self.env['account.account']
        invoice_obj = self.env['account.move']
        company_obj = self.env['res.company']
        currency_obj = self.env['res.currency']
        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            if i >= 1:
                print(i)
                company = self.ap_company_id or company_obj.search([('name', '=', field[4])], limit = 1)
                date = datetime.strptime(field[6], '%d/%m/%Y')
                partner = partner_obj.sudo().with_company(company).search([('name', '=', field[5]), '|', ('company_id','=',company.id), ('company_id', '=', False)], limit = 1)
                account = account_obj.sudo().with_company(company).search([('company_id', '=', company.id), ('code', '=', '500010')], limit = 1)
                currency = currency_obj.sudo().with_company(company).search([('symbol','=',field[7])],limit=1)
                price_unit = field[12]
                
                price_unit = price_unit.replace(',', '')
                price_unit = price_unit.replace(" ",'')
                if price_unit == '-':
                    price_unit = price_unit.replace('-','0.0')
                price_unit = float(price_unit)
                tax_ids = field[14]
                tax_ids = field[14].replace('%','')
                if not field[14] or field[14] in ['0', 0]:
                    tax_ids = self.env['account.tax'].sudo().with_company(company).search([('name', '=', 'Zero Rate'), '|', ('company_id', '=', company.id), ('company_id', '=', False)], limit = 1)
                else:
                    tax_ids = self.env['account.tax'].sudo().with_company(company).search([('name', '=', 'Standard Rate'), '|', ('company_id', '=', company.id), ('company_id', '=', False)], limit = 1)
                journal = self.env['account.journal'].sudo().with_company(company).search([('company_id', '=', company.id),('name', '=', 'Customer Invoices')], limit = 1)
                if partner and company and price_unit > 0:
                    inv_line_vals = {
                            'account_id': journal.default_account_id.id,
                            'name': 'opening balance' ,
                            'price_unit': price_unit,
                            'quantity': 1,
                            'company_id' : company.id,
                            'tax_ids' : [(6,0, tax_ids.ids)],
                            'currency_id': company.currency_id.id,
                        
                        }
                    
                   
                    
                    inv = self.env["account.move"].with_company(company).create({
                        'doc_id':field[0],
                        'doc_type':field[1],
                        'doc_no':field[2],
                        "move_type": 'out_invoice',
                        "invoice_date_due": date,
                        "invoice_date": date,
                        "date": date,                
                        'ref': field[3],
                        'journal_id': journal.id,
                        'partner_id': partner.id,
                        'invoice_line_ids': [(0,0,inv_line_vals)],
                        'company_id' : company.id,
                        'currency_id': company.currency_id.id,
                    })
                    inv.with_company(company).action_post()
                else:
                    if not partner:
                        self.env['account.import.issue'].create({'issue':'customer not found', 'ap_company_id': company.id,'row_data':field})
                        print('customer not found...................',field[5])
                    else:
                        self.env['account.import.issue'].create({'issue':'PRICE less than zero', 'ap_company_id': company.id,'row_data':field})
                        print('price not found...................',field[5])


class AccountMove(models.Model):

    _inherit = 'account.move'

    doc_id = fields.Integer(string="Doc Id")
    doc_type = fields.Char(string="Doc Type")
    doc_no = fields.Integer(string="Doc No.")

class IssueDebtorImport(models.Model):

    _name = 'account.import.issue'

    issue = fields.Char(string = "Issue")
    ap_company_id = fields.Many2one("res.company", string = "Company")
    row_data = fields.Text(String = "Row Data")
