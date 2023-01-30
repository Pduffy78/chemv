from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta



class ir_config_parameter(models.Model):
    _inherit = 'ir.config_parameter'
    
    
    
    # def create(self, vals):
    #     if vals.get('key') == 'web.base.url' and vals.get('value'):
    #         param = self.env.ref('ap_system_parameter.demo_chemv_params')
    #         vals.update({'value': param.value})
    #     res = super(ir_config_parameter, self).create(vals)
    
    
    def write(self, vals):
        for record in self:
            if vals.get('key') == 'web.base.url' or vals.get('value') == 'https://pduffy78-chemv.odoo.com':
                param = self.env.ref('ap_system_parameter.demo_chemv_params')
                vals.update({'value': param.value})
        res = super(ir_config_parameter, self).write(vals)
        