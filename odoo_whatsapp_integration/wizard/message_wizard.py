from odoo import models, fields, api, _
import html2text
import urllib.parse as parse

class MessageError(models.TransientModel):
    _name='display.error.message'
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get('message')
        return False
    name = fields.Text(string="Message", readonly=True, default=get_message)

class SendMessage(models.TransientModel):
    _name = 'whatsapp.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).partner_id)
    mobile_number = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True)

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        print("res_id",res_id)
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        print("values22222222",values)
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    
    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']

        returned_fields = fields + ['partner_ids']
        values = {}

        template = self.env['mail.template'].browse(template_id)
        print("temp;;;;",template)

        for res_id in res_ids:
            record = self.env[template.model].browse(res_id)
            print("rec",record)
            values[res_id] = {}

            for field in fields:
                values[res_id][field] = template._render_field(field, [res_id])[res_id]

            values[res_id]['partner_ids'] = [record.partner_id.id] if record.partner_id else []
            values[res_id]['message'] = html2text.html2text(values[res_id].get('body_html', ''))

        return values if multi_mode else values[res_ids[0]]


    def send_custom_message(self):
        if self.message and self.mobile_number:
            message_string = parse.quote(self.message)
            message_string = message_string[:(len(message_string) - 3)]
            number = self.user_id.mobile
            link = "https://web.whatsapp.com/send?phone=" + number
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
            return send_msg