# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"

    location_transit_id = fields.Many2one("stock.location", string="End Location")
    is_transit = fields.Boolean(string="Transit?")

    def button_validate(self):
        if self.location_transit_id and self.location_dest_id and not self.is_transit == True:
            picking_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])
            if picking_count == 0:
                self.button_create_new_transfer()
                return super(Picking, self).button_validate()
            else:
                return super(Picking, self).button_validate()
        else:
            return super(Picking, self).button_validate()

    def button_create_new_transfer(self):
        picking_id = self.copy()
        if picking_id:
            picking_id.update({
                "location_id": self.location_dest_id.id,
                "location_dest_id": self.location_transit_id.id,
                "is_transit": True,
                "origin": self.name,
                "move_line_ids_without_package": False,
                "move_line_ids": False,
                "move_line_nosuggest_ids": False 
            })

    def button_view_created_transfer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfer',
            'view_type': 'form',
            'view_mode': "tree,form",
            'view_id': False,
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],
            # 'context': "{'create': False}"
        }
