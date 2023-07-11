from odoo import models, fields, api, _
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
    
class import_inventory_adjustment(models.TransientModel):
    _name = 'import.inventory.adjustment'

    upload_csv = fields.Binary(string="Upload XLSX file")
    
    
    
    def read_xls_book(self):
        
        book = xlrd.open_workbook(file_contents=base64.decodebytes(self.upload_csv) or b'')
        sheet_name = book.sheet_names()
        sheet_name = sheet_name and sheet_name[0] or 'Sheet1'
        sheet = book.sheet_by_name(sheet_name)
        rows = []
        location_obj = self.env["stock.location"]
        product_obj = self.env["product.product"]
        uom_obj = self.env["uom.uom"]
        quant_obj = self.env["stock.quant"]
        # emulate Sheet.get_rows for pre-0.9.4
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            location = location_obj.search([('complete_name', '=', row[0].value)], limit = 1)
            prod_str = row[1] and row[1].value or ''
            prod_str = prod_str and prod_str.split('[')
            prod_str = prod_str and len(prod_str) > 1 and prod_str[1] or ''
            prod_str = prod_str and len(prod_str) > 1 and prod_str.split(']')[0] or ''
            print(prod_str)
            product = product_obj.search([('default_code', '=', prod_str)], limit = 1)
            lot = row[3].value
            uom = uom_obj.search([('name', '=', row[5].value)])
            inv_qnt = row[6].value
            # if product and product.tracking != 'none':
            #     raise ValidationError('The product with tracking not allowed to import: ' + str(product.name))
            if location and product and product.tracking == 'none':
                quants = quant_obj.search([('location_id', '=', location.id), ('product_id', '=', product.id)])
                for quant in quants:
                    qnnt = quant.with_context(inventory_mode=True)
                    qnnt.inventory_quantity = float(inv_qnt)
                    # quant._update_available_quantity(product, location,float(inv_qnt))
                    quant._onchange_location_or_product_id()
                if not quants:
                    quant_obj.with_context(inventory_mode=True).create({
                                                                        'product_id': product.id,
                                                                        'inventory_quantity': float(inv_qnt),
                                                                        'location_id': location.id,
                                                                        })
    
    def do_open_records(self):
        print()