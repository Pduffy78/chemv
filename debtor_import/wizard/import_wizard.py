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

    

class wizard_import_ap(models.TransientModel):
    _name = 'wizard.import.ap'
    
    upload_csv = fields.Binary(string="Upload csv file")
    
        
        
    
    
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
        print(1111111111111111111111111111)
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
        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            if i >= 1:
                date = datetime.strptime(field[7], '%m/%d/%y')
                partner = partner_obj.sudo().search([('name', '=', field[5])], limit = 1)
                company = company_obj.search([('name', '=', field[4])], limit = 1)
                account = account_obj.sudo().search([('company_id', '=', company.id), ('code', '=', '500010')], limit = 1)
                price_unit = field[10]
                price_unit = price_unit.replace(',', '')
                price_unit = float(price_unit)
                tax_ids = field[11]
                if not field[11] or field[11] in ['0', 0]:
                    tax_ids = self.env['account.tax'].sudo().search([('name', '=', 'Zero Rate'), ('company_id', '=', company.id)], limit = 1)
                else:
                    tax_ids = self.env['account.tax'].sudo().search([('name', '=', 'Standard Rate'), ('company_id', '=', company.id)], limit = 1)
                journal = self.env['account.journal'].sudo().search([('name', '=', 'Cus Inv Opening Balance'), ('company_id', '=', company.id)], limit = 1)
                inv_line_vals = {
                        'account_id': journal.default_account_id.id,
                        'name': 'opening balance' ,
                        'price_unit': price_unit,
                        'quantity': 1,
                        'company_id' : company.id,
                        # 'product_id': False,
                        'tax_ids' : [(6,0, tax_ids.ids)],
                        'currency_id': company.currency_id.id,
                    
                    }
                print(inv_line_vals)
                inv = self.env["account.move"].create({
                    # "name": inv_line.inv_number,
                    "move_type": 'out_invoice',
                    "invoice_date_due": date,
                    "invoice_date": date,
                    "date": date,                
                    'ref': field[3],
                    'journal_id': journal.id,
                    'partner_id': partner.id,
                    'invoice_line_ids': [(0,0,inv_line_vals)],
                    'company_id' : company.id,
                    # 'tax_line_ids': False,
                    # 'currency_id': currency.id,
                    'currency_id': company.currency_id.id,
                    # 'account_id': journal_invoice.default_debit_account_id.id,
                })
                
                inv.action_post()
#                 domain = []
#                 if field[0]:
#                     domain += [('name', '=', field[0])]
#                 elif field[1]:
#                     domain += [('email', '=', field[1])]
#                 domain_parent = []
#                 if field[3]:
#                     domain_parent += [('name', '=', field[3])]
#                 elif field[4]:
#                     domain_parent += [('email', '=', field[4])]
#                 current_partner = partner_obj.search(domain,limit = 1)
#                 current_parent = partner_obj.search(domain_parent,limit = 1)
#                 if current_partner and current_parent:
#                     if current_partner != current_parent:
#                         current_partner.parent_id = current_parent
