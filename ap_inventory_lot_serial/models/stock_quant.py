# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import http

class StockQuant(models.Model):
    _inherit = "stock.quant"

    # @api.model
    # def create(self,vals):
    #     res = super(StockQuant,self).create(vals)
    #     # print("\n\n\nstock Quant Method Called?>>>>>>>>>>>>>>>\n\n\n",vals,res)

    #     return res

class BaseImport(models.TransientModel):

    _inherit = 'base_import.import'

    def execute_import(self, fields, columns, options, dryrun=False):
        
        if self.res_model == 'stock.quant':
            
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            
            try:
                input_file_data, import_fields = self._convert_import_data(fields, options)
                
                # Parse date and float field
                input_file_data = self._parse_import_data(input_file_data, import_fields, options)
            except ImportValidationError as error:
                return {'messages': [error.__dict__]}
            import_fields, merged_data = self._handle_multi_mapping(import_fields, input_file_data)
            for rec in merged_data:
                
                if rec[2] != '':
                    lot_id = self.env['stock.lot'].search([('name','=',rec[2].strip())])
                    
                    # location_id = self.env['stock.location'].search([('display_name','=',rec[0].strip())])
                    # split_string = rec[1].split("]")
                    
                    product_id = self.env['product.product'].search([('name','=',rec[1].strip())])
                   
                    # stock_quant = self.env['stock.quant'].search([('lot_id','=',lot_id.id)])
                    # print("\n\n\nstock_quant00000000000>>>>>>>>",stock_quant)
                    if not lot_id:
                        location_id = self.env['stock.location'].search([])
                        location_id = location_id.filtered(lambda x:x.display_name == rec[0].strip())
                        
                        split_string = rec[1].split("]")
                        product_id = self.env['product.product'].search([('name','=',split_string[1].strip())])
                        
                        self.env['stock.lot'].create({
                                'name':rec[2].strip(),
                                'product_id':product_id.id,
                                'company_id':self.env.company.id
                            })
                        self.env['stock.quant'].create({

                                'product_id':product_id.id,
                                'inventory_quantity':rec[3],
                                'location_id':location_id.id,
                                'user_id':self.env.user.id,
                                'lot_id':lot_id.id
                            })

        res = super(BaseImport,self).execute_import(fields, columns, options, dryrun=False)            
        return res
   