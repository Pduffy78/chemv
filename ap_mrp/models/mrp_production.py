# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MRPProduction(models.Model):
    _inherit = "mrp.production"


    def button_mark_done(self):
        child_ids_list = self.get_mo_child()
        for child_id in child_ids_list[::-1]:
            child_id.button_mark_done()
        res = super(MRPProduction, self).button_mark_done()
        return res 


    def get_mo_child(self):
        child_ids_list = []
        mrp_production_ids = self._get_children().ids
        for mrp_production_id in mrp_production_ids:
            mrp_id = self.env["mrp.production"].browse(mrp_production_id)
            child_ids_list.append(mrp_id)
            # Level 1
            if mrp_id.mrp_production_child_count != 0:
                mrp_production_ids_1 = mrp_id._get_children().ids
                for mrp_production_id_1 in mrp_production_ids_1:
                    mrp_id_1 = self.env["mrp.production"].browse(mrp_production_id_1)
                    child_ids_list.append(mrp_id_1)
                    # Level 2
                    if mrp_id_1.mrp_production_child_count != 0:
                        mrp_production_ids_2 = mrp_id_1._get_children().ids
                        for mrp_production_id_2 in mrp_production_ids_2:
                            mrp_id_2 = self.env["mrp.production"].browse(mrp_production_id_2)
                            child_ids_list.append(mrp_id_2)
                            # Level 3
                            if mrp_id_2.mrp_production_child_count != 0:
                                mrp_production_ids_3 = mrp_id_2._get_children().ids
                                for mrp_production_id_3 in mrp_production_ids_3:
                                    mrp_id_3 = self.env["mrp.production"].browse(mrp_production_id_3)
                                    child_ids_list.append(mrp_id_3)
                                    # Level 4
                                    if mrp_id_3.mrp_production_child_count != 0:
                                        mrp_production_ids_4 = mrp_id_3._get_children().ids
                                        for mrp_production_id_4 in mrp_production_ids_4:
                                            mrp_id_4 = self.env["mrp.production"].browse(mrp_production_id_4)
                                            child_ids_list.append(mrp_id_4)
                                            # Level 5
                                            if mrp_id_4.mrp_production_child_count != 0:
                                                mrp_production_ids_5 = mrp_id_4._get_children().ids
                                                for mrp_production_id_5 in mrp_production_ids_5:
                                                    mrp_id_5 = self.env["mrp.production"].browse(mrp_production_id_5)
                                                    child_ids_list.append(mrp_id_5)
                                                # Level 6
                                                if mrp_id_5.mrp_production_child_count != 0:
                                                    mrp_production_ids_6 = mrp_id_5._get_children().ids
                                                    for mrp_production_id_6 in mrp_production_ids_6:
                                                        mrp_id_6 = self.env["mrp.production"].browse(mrp_production_id_6)
                                                        child_ids_list.append(mrp_id_6)
        sorted_list = sorted(child_ids_list)                                                
        return sorted_list