from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class ResPartner(models.Model):
	_inherit = 'res.partner'

	follow_up = fields.Boolean(string="Follow Up")

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.model
	def create(self,vals):
		res = super(SaleOrder,self).create(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.follow_up and partner_id.followup_level.name == 'Firendly Reminder Email':
			raise ValidationError('you are not able to create')
		return res

	def write(self,vals):
		res = super(SaleOrder,self).write(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.follow_up and partner_id.followup_level.name == 'Firendly Reminder Email':
			raise ValidationError('you are not able to create')
		return res

class AccountMove(models.Model):
	_inherit = 'account.move'

	@api.model
	def create(self,vals):
		res = super(AccountMove,self).create(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.follow_up and partner_id.followup_level.name == 'Firendly Reminder Email':
			raise ValidationError('you are not able to create')
		return res

	def write(self,vals):
		res = super(AccountMove,self).write(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.follow_up and partner_id.followup_level.name == 'Firendly Reminder Email':
			raise ValidationError('you are not able to create')
		return res
