from odoo import models, fields, api, _



class MassMailingContact(models.Model):
    _inherit = "mailing.contact"

    cellphone = fields.Char(string = "Cellphone")
    
    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2',readonly=False)
    zip = fields.Char('Zip',readonly=False)
    city = fields.Char('City',readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',readonly=False,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',readonly=False)