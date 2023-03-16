from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class ResPartner(models.Model):
	_inherit = 'res.partner'

	is_follow_up_new = fields.Boolean(string="Follow Up",compute="_compute_is_follow_up",inverse="_inverse_is_follow_up",store=True)
	

	@api.depends('followup_level')
	def _compute_is_follow_up(self):
		
		for rec in self:
			if rec.followup_level.name in ['Friendly Reminder Email','First reminder email','Second Reminder Email']:
				rec.is_follow_up_new = True
			else:
				rec.is_follow_up_new = False

	
	def _inverse_is_follow_up(self):
		print("\n\n\nyes...........>>>>>>>>>>>mmmmmmmmmmmmm\n\n\n",self)
		

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.model
	def create(self,vals):
		res = super(SaleOrder,self).create(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.is_follow_up_new:
			raise ValidationError('You are Not Allowed To Create Sale')
		return res

	def write(self,vals):
		res = super(SaleOrder,self).write(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.is_follow_up_new:
			raise ValidationError('You are Not Allowed To Edit Sale')
		return res

class AccountMove(models.Model):
	_inherit = 'account.move'

	@api.model
	def create(self,vals):
		res = super(AccountMove,self).create(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.is_follow_up_new:
			raise ValidationError('You are Not Allowed To Create Invoice')
		return res

	def write(self,vals):
		res = super(AccountMove,self).write(vals)
		partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
		if partner_id.is_follow_up_new:
			raise ValidationError('You are Not Allowed To Edit Invoice')
		return res
