import os
import csv
import base64
import re
from io import StringIO
from odoo import api, fields, models, tools, SUPERUSER_ID, _

import base64
from odoo.exceptions import UserError, ValidationError
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None
    
class EmailImportWizard(models.TransientModel):
    _name = "email.import.wizard"
    _description = "Email Import Wizard"

    upload_xls_file = fields.Binary(string="Upload XLS File")
    mail_list_id = fields.Many2one("mailing.list", string="Mail List")
    

    def btn_import_email_records(self):
        print("Button is calling.................................")
        if self.upload_xls_file:
            book = xlrd.open_workbook(file_contents=base64.decodebytes(self.upload_xls_file) or b'')
            sheet_name = book.sheet_names()
            sheet_name = sheet_name and sheet_name[0] or 'Sheet1'
            sheet = book.sheet_by_name(sheet_name)
            rows = []
            # mailiing_list_obj = self.env["mailing.list"]
            mailing_contact_obj = self.env["mailing.contact"]
            tag_obj = self.env["res.partner.category"]
            # emulate Sheet.get_rows for pre-0.9.4
            for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
                name = str(row[1].value)
                email = row[0].value
                # cellphone = row[4].value or row[12].value
                # street = row[8].value
                # city = row[7].value
                # zip = row[9].value
                company_name = row[2].value
                # tag_ids = row[6].value
                # tag_ids = tag_ids.split(',')
                # tag_ids_list = []
                # for tag in tag_ids:
                #     if tag:
                #         exst_tag = tag_obj.search([('name', '=', tag)], limit = 1)
                #         if not exst_tag and tag:
                #             new_tag = tag_obj.create({'name' : tag})
                #             tag_ids_list.append(new_tag.id)
                #         else:
                #             tag_ids_list.append(exst_tag.id)
                # tag_ids = [(6, 0, tag_ids_list)]
                subscription_list_ids = [(0, 0, {'list_id' : self.mail_list_id.id})]
                mailing_contact_obj.create({
                    'name' : name,
                    'email' : email,
                    # 'cellphone' : cellphone,
                    # 'street' : street,
                    # 'city' : city,
                    # 'zip' : zip,
                    'company_name' : company_name,
                    # 'tag_ids' : tag_ids,
                    'subscription_list_ids' : subscription_list_ids,
                    })



