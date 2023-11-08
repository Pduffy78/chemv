from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from datetime import datetime
from odoo.tools import  DEFAULT_SERVER_DATETIME_FORMAT


class tyre_details(models.Model):
    _name = 'tyre.details'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _rec_name = "name"
    
    name = fields.Char(string='Number', copy=False, index=True, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the Tyre Details without removing it.")
    date = fields.Date(
        string='Date',
        tracking=True,
        default=fields.Date.context_today
    )
    new_text = fields.Text(string='New Text')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)
    notes = fields.Text(string='Notes')
    sequence = fields.Integer(string='Sequence')
    make = fields.Selection(selection=[
            ('michelin', 'Michelin'),
            ('bridgestone', 'Bridgestone'),
            ('Goodyear', 'goodyear'),
        ], string='Tyre Make:', tracking=True)
    rating = fields.Selection(selection=[
            ('e1', 'E1'),
            ('e2', 'E2'),
            ('e3', 'E3'),
            ('e4', 'E4'),
            ('e7', 'E7'),
        ], string='Tyre Rating:', tracking=True)
    size = fields.Selection(selection=[
            ('59/80R63', '59/80R63'),
            ('53/80R63', '53/80R63'),
            ('50/90R57', '50/90R57'),
            ('50/80R57', '50/80R57'),
            ('40.00R57', '40.00R57'),
            ('37.00R57', '37.00R57'),
            ('36.00R57', '36.00R57'),
            ('33.00R57', '33.00R57')
        ], string='Tyre Size:', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    job_card_count = fields.Integer(string='Jobcard Count', compute='_get_jobcard')
    
    def _get_jobcard(self):
        for tyre in self:
            tyre.job_card_count = len(self.env['job.cards.studio'].search([('tyre_detail_id', '=', self.id)]).ids)
    
    def action_view_jobcard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Job Cards'),
            'res_model': 'job.cards.studio',
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('tyre_detail_id', '=', self.id)],
        }
    
    def create_job_card(self):
        self.env['job.cards.studio'].create( {
            'tyre_detail_id' : self.id,
            'tyre_name' : self.name,
            'tyre_notes' : self.notes,
            'tyre_company_id' : self.company_id and self.company_id.id or False,
            'tyre_rating' : self.rating or '',
            'tyre_size' : self.size or '',
            'tyre_user_id' : self.user_id and self.user_id.id or False,
            'tyre_date' : self.date or False,
            'tyre_make' : self.make or '',
            'tyre_rating' : self.rating or '',
            })

class job_cards_studio(models.Model):
    _name = 'job.cards.studio'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _rec_name = "name"
    
    active = fields.Boolean(default=True, help="Set active to false to hide the Tyre Details without removing it.")
    color = fields.Integer(string='Color')
    name = fields.Char(string='Number', copy=False, index=True, tracking=True, default=lambda self: self.env['ir.sequence'].next_by_code('job.cards.studio'))
    air_bags_checked = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Air Bags Checked?', tracking=True)   
    airline_fittings_condition = fields.Selection(selection=[
            ('good', 'Yes'),
            ('leaking', 'Leaking'),
            ('poor', 'Poor'),
        ], string='Airline Fittings Condition:', tracking=True)
    application_1 = fields.Binary(string='Application 1')
    application_2 = fields.Binary(string='Application 2')
    application_3 = fields.Binary(string='Application 3')
    application_4 = fields.Binary(string='Application 4')
    bead_to_bead_alignment = fields.Boolean(string = 'Bead to Bead Alignment')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)
    control_box_connections =  fields.Selection(selection=[
            ('good', 'Yes'),
            ('poor', 'Poor'),
        ], string='Control Box Connections:', tracking=True)
    control_box_number = fields.Char(string='Control Box Number:', copy=False, tracking=True)
    cosmetic_finish = fields.Selection(selection=[
            ('good', 'Yes'),
            ('revise', 'Revise'),
        ], string='Cosmetic Finish:', tracking=True)
    curing_set_up_1 = fields.Binary(string='Curing Set up 1')
    curing_set_up_2 = fields.Binary(string='Curing Set up 2')
    final_pic_1 = fields.Binary(string='Final Pic 1 ')
    final_pic_2 = fields.Binary(string='Final Pic 2 ')
    final_pic_3 = fields.Binary(string='Final Pic 3 ')
    final_pic_4 = fields.Binary(string='Final Pic 4 ')
    prep_image_1 = fields.Binary(string='Prep Image 1')
    prep_image_2 = fields.Binary(string='Prep Image 2')
    prep_image_3 = fields.Binary(string='Prep Image 3')
    prep_image_4 = fields.Binary(string='Prep Image 4')
    supervisor = fields.Binary(string='Supervisor')
    image = fields.Binary(string='Image')
    initial_inspection_1 = fields.Binary(string='Initial Inspection 1:')
    initial_inspection_2 = fields.Binary(string='Initial Inspection 2:')
    curing_time_hours = fields.Integer(string='Curing Time Hours:')
    date = fields.Date(
        string='Date Received',
        tracking=True,
        default=fields.Date.context_today
    )
    date_start = fields.Datetime(
        string='Start Date',
        tracking=True,
    )
    date_stop = fields.Datetime(
        string='End Date',
        tracking=True,
    )
    depth_mm = fields.Integer(string='Depth mm')
    electrical_connections =  fields.Selection(selection=[
            ('good', 'Yes'),
            ('poor', 'Poor'),
        ], string='Electrical Connections:', tracking=True)
    
    evidence_of_rust = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Evidence of Rust:', tracking=True)
    first_coat_applied = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='First Coat Applied', tracking=True)
    gouging_completed = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Gouging completed:', tracking=True)
    harness_strapped_correctly = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Harness Strapped Correctly?', tracking=True)
    heat_pads_checked= fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Heat Pads Checked?', tracking=True)
    
    injury_position = fields.Selection(selection=[
            ('sidewall', 'Sidewall'),
            ('shoulder', 'Shoulder'),
            ('crown', 'Crown')
        ], string='Injury Position', tracking=True)
    injury_type = fields.Selection(selection=[
            ('minor', 'Minor'),
            ('medium', 'Medium'),
            ('major', 'Crown')
        ], string='Injury Type', tracking=True)
    inner_liner_removed = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Inner Liner Removed?', tracking=True)
    kanban_state = fields.Selection(selection=[
            ('normal', 'Yes'),
            ('done', 'No'),
            ('blocked', 'Blocked'),
        ], string='Kanban State', tracking=True)
    length_mm = fields.Integer(string='Length mm')
    tyre_detail_id = fields.Many2one('tyre.details', string = "Tyre Details")
    no_of_cables_removed = fields.Integer(string='No of Cables Removed:')
    notes = fields.Char(string = 'Notes')
    number_of_major_repairs = fields.Selection(selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4')
        ], string='Number of major repairs', tracking=True)
    outer_cure = fields.Selection(selection=[
            ('good', 'Good'),
            ('not_completely_cured', 'Not Completely Cured'),
        ], string='Outer Cure:', tracking=True)
    overall_tyre_condition = fields.Selection(selection=[
            ('Excellent', 'Excellent'),
            ('Good', 'Good'),
            ('Medium wear and tear', 'Medium wear and tear'),
            ('Poor condition', 'Poor condition')
        ], string='Overall Tyre Condition:', tracking=True)
    
    overbuff_border = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Overbuff Border:', tracking=True)
    patch_cure = fields.Selection(selection=[
            ('good', 'Good'),
            ('not_completely_cured', 'Not Completely Cured'),
        ], string='Patch Cure:', tracking=True)
    pressure_inner_air_bag_1 = fields.Float(string = 'Pressure Inner air bag:')
    pressure_outer_air_bag = fields.Float(string = 'Pressure Outer Air Bag:')
    previous_repairs = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Previous Repairs?', tracking=True)
    priority = fields.Boolean(string = 'High Priority')
    repair_area_cleaned = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Repair Area Cleaned?', tracking=True)
    work_area_cleaned = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Work Area Cleaned?', tracking=True)
    repair_unit_used = fields.Char(string = 'Repair Unit Used:')
    repairs_note = fields.Html(string = 'Repairs Note:')
    rope_rubber_batch_no = fields.Char(string = 'Rope Rubber Batch No:')
    second_coat_applied = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Second Coat Applied', tracking=True)
    sequence = fields.Integer(string='Sequence')
    shaping_of_injury = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Shaping of Injury:', tracking=True)
    shore_hardness = fields.Integer(string='Shore Hardness:')
    stage_id = fields.Many2one('job.cards.studio.stage', string = 'Stage')
    steel_cable_damage = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Steel Cable Damage:', tracking=True)
    steel_cord_insert = fields.Selection(selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ], string='Steel Cord Insert:', tracking=True)
    tag_ids = fields.Many2many('job.cards.studio.tag', 'job_card_tag_studio_rel', 'job_card_id', 'tag_id', string = 'tags')
    temperature_setting = fields.Selection(selection=[
            ('120 Deg C', '120 Deg C'),
            ('125 Deg C', '125 Deg C'),
            ('130 Deg C', '130 Deg C'),
            ('135 Deg C', '135 Deg C')
        ], string='Temperature Setting:', tracking=True)
    
    
    tread_depth_mm = fields.Integer(string='Tread Depth mm')
    user_id = fields.Many2one('res.users', string = 'Responsible')
    vulc_cement_batch_number = fields.Char(string='Vulc Cement Batch Number:')
    width_mm = fields.Integer(string='Width mm')
    new_lines = fields.Char(string='New Lines')
    #tyre fileds
    tyre_name = fields.Char(string='Number', copy=False, index=True, tracking=True)
    tyre_date = fields.Date(
        string='Date',
        tracking=True,
        default=fields.Date.context_today
    )
    tyre_company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)
    tyre_notes = fields.Text(string='Notes')
    tyre_make = fields.Selection(selection=[
            ('michelin', 'Michelin'),
            ('bridgestone', 'Bridgestone'),
            ('Goodyear', 'goodyear'),
        ], string='Tyre Make:', tracking=True)
    tyre_rating = fields.Selection(selection=[
            ('e1', 'E1'),
            ('e2', 'E2'),
            ('e3', 'E3'),
            ('e4', 'E4'),
            ('e7', 'E7'),
        ], string='Tyre Rating:', tracking=True)
    tyre_size = fields.Selection(selection=[
            ('59/80R63', '59/80R63'),
            ('53/80R63', '53/80R63'),
            ('50/90R57', '50/90R57'),
            ('50/80R57', '50/80R57'),
            ('40.00R57', '40.00R57'),
            ('37.00R57', '37.00R57'),
            ('36.00R57', '36.00R57'),
            ('33.00R57', '33.00R57')
        ], string='Tyre Size:', tracking=True)
    tyre_user_id = fields.Many2one('res.users', string='Responsible')
    
  
class job_cards_studio_tag(models.Model):
    _name = 'job.cards.studio.tag'  

    color = fields.Integer(string='Color')
    name = fields.Char(string='Number', copy=False)

class job_cards_studio_stage(models.Model):
    _name = 'job.cards.studio.stage'
    
    name = fields.Char(string='Name', copy=False)
    sequence = fields.Integer(string='Sequence')

class risk_assessments_studio_tag(models.Model):
    _name = 'risk.assessments.studio.tag'  

    color = fields.Integer(string='Color')
    name = fields.Char(string='Name', copy=False)

class risk_assessments_studio(models.Model):
    _name = 'risk.assessments.studio'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _rec_name = "name"


    active = fields.Boolean(default=True, help="Set active to false to hide the Risk Assessment without removing it.")
    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name', copy=False, index=True, tracking=True)
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string = 'Responsible')
    date = fields.Date(
        string='Date',
        tracking=True,
        default=fields.Date.context_today
    )
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)
    tag_ids = fields.Many2many('risk.assessments.studio.tag', 'risk_asses_tag_rel', 'job_card_id', 'tag_id', string = 'tags')
    assessments_line_ids = fields.One2many('assessments.line.studio' , 'assessment_id', string = 'Assessment Lines')


class assessments_line_studio(models.Model):
    _name = 'assessments.line.studio' 

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Description', copy=False, index=True, tracking=True)
    assessment_id = fields.Many2one(comodel_name='risk.assessments.studio', string='Assessment')




