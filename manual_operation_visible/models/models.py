# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class manual_operation_visible(models.Model):
#     _name = 'manual_operation_visible.manual_operation_visible'
#     _description = 'manual_operation_visible.manual_operation_visible'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
