from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet


class Inventory(models.Model):
    _name = "stock.inventory.inherit"
    _description = "Inventory"
    _order = "date desc, id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Inventory Reference', default="Inventory",
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    product_categ_id = fields.Many2one('product.category',string="Product Category")
    date = fields.Datetime(
        'Inventory Date',
        readonly=True, required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
             "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.")
    
    move_ids = fields.One2many(
        'stock.move', 'inventory_id', string='Created Moves',
        states={'done': [('readonly', True)]})
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('done', 'Validated')],
        copy=False, index=True, readonly=True, tracking=True,
        default='draft')
    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)
    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]")
    product_ids = fields.Many2many(
        'product.product', string='Products', check_company=True,
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Products to focus your inventory on particular Products.")
    start_empty = fields.Boolean('Empty Inventory',
        help="Allows to start with an empty inventory.")
    prefill_counted_quantity = fields.Selection(string='Counted Quantities',
        help="Allows to start with a pre-filled counted quantity for each lines or "
        "with all counted quantities set to zero.", default='counted',
        selection=[('counted', 'Default to stock on hand'), ('zero', 'Default to zero')])
    exhausted = fields.Boolean(
        'Include Exhausted Products', readonly=True,
        default=True,
        # states={'draft': [('readonly', False)]},
        help="Include also products with quantity of 0")
    
    
    @api.onchange('product_categ_id')
    def onchange_product_categ_id(self):
        if self.product_categ_id:
            self.product_ids = self.env['product.product'].search([('categ_id','=',self.product_categ_id.id),('detailed_type','=','product')])
    
    @api.onchange('company_id')
    def _onchange_company_id(self):
        # If the multilocation group is not active, default the location to the one of the main
        # warehouse.
        if not self.user_has_groups('stock.group_stock_multi_locations'):
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            if warehouse:
                self.location_ids = warehouse.lot_stock_id

    def copy_data(self, default=None):
        name = _("%s (copy)") % (self.name)
        default = dict(default or {}, name=name)
        return super(Inventory, self).copy_data(default)       

    def action_start(self):
        self.ensure_one()
        
        self._check_company()
        return self.action_open_inventory_lines()

    
    def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Inventory Lines'),
            'res_model': 'stock.quant',
        }
        context = {
            'default_is_editable': True,
            'default_inventory_id': self.id,
            'default_company_id': self.company_id.id,
           'hide_location': True,
           'inventory_mode': True, 
           'no_at_date': True, 
           'bin_size': True 
        }
        # Define domains and context
        domain = [
            
            ('product_id', 'in', self.product_ids.ids),
            ('location_id.usage', 'in', ['internal', 'transit'])
        ]
        if self.location_ids:
            location_ids = self.location_ids.ids
        else:
            location_ids = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)]).lot_stock_id.ids
        
        Quants = self.env['stock.quant'].with_context(context).search(domain)
        
        Quants = Quants.mapped('product_id')
        for rec in self.product_ids:
            if rec.id not in Quants.ids:
                self.env['stock.quant'].create({
                        'inventory_id': self.id,
                        'product_id': rec.id,
                        'location_id': location_ids[0],
                        'user_id':self.env.user.id,
                        'quantity': 0
                    })
        
        if self.location_ids:
            context['default_location_id'] = self.location_ids[0].id
            if len(self.location_ids) == 1:
                if not self.location_ids[0].child_ids:
                    context['readonly_location_id'] = True
            
        if self.product_ids:
            # no_create on product_id field
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree_inventory_editable').id
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id
            action['context'] = context
            action['domain'] = domain
        else:
            # no product_ids => we're allowed to create new products in tree
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree_inventory_editable').id
            domain = [('location_id.usage', 'in', ['internal', 'transit'])]
            action['context'] = context
            action['domain'] = domain

        
        return action
    
class StockMove(models.Model):
    
    _inherit = 'stock.move'
    
    inventory_id = fields.Many2one('stock.inventory.inherit')


class stock_quant(models.Model):
    
    _inherit = 'stock.quant'
    
    inventory_id = fields.Many2one('stock.inventory.inherit')
    
    def action_update_apply(self):
        for rec in self:
            rec.action_apply_inventory()
    
    @api.model
    def create(self, vals):
        res = super(stock_quant, self).create(vals)
        res._onchange_location_or_product_id()
        if self._is_inventory_mode():
            res._check_company()
        return res