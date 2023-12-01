# Copyright 2018 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
import base64


class OutstandingStatementWizard(models.TransientModel):
    """Outstanding Statement wizard."""

    _name = "outstanding.statement.wizard"
    _inherit = "statement.common.wizard"
    _description = "Outstanding Statement Wizard"

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_statement()
        if report_type == "xlsx":
            report_name = "p_s.report_outstanding_statement_xlsx"
        else:
            report_name = "partner_statement.outstanding_statement"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)

    def button_send_mail(self):
        
        mail_temp_obj = self.env['mail.template']
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']
        if self._context['active_ids']:
            for partner in self.env['res.partner'].browse(self._context['active_ids']):
                
                
                attachments = []
                data = self._prepare_statement()
                data['partner_ids'] = [partner.id]
                
                template = self.env.ref('partner_statement.action_print_outstanding_statement', False)
                report_name = template.report_name
                report = template
                report_service = template.report_name

                if report.report_type in ['qweb-html', 'qweb-pdf']:
                    result, format = report._render_qweb_pdf('partner_statement.outstanding_statement',[partner.id],data=data)
                else:
                    res = report._render([res_id])
                    if not res:
                        raise UserError(_('Unsupported report type %s found.', report.report_type))
                    result, format = res

                # TODO in trunk, change return format to binary to match message_post expected format
                result = base64.b64encode(result)
                if not report_name:
                    report_name = 'report.' + report_service
                ext = "." + format
                if not report_name.endswith(ext):
                    report_name += ext
                attachments.append((report_name, result))
                recipient_ids = [(4, partner.id) ]
#                 values.update(email_values or {})
                attachment_ids = []
                attachments = attachments
                mail = Mail.create({})
                for attachment in attachments:
                    attachment_data = {
                        'name': attachment[0],
                        # 'datas_fname': attachment[0],
                        'datas': attachment[1],
                        'type': 'binary',
                        'res_model': 'mail.message',
                        'res_id': mail.mail_message_id.id,
                    }
                    kk = Attachment.create(attachment_data).id
                    attachment_ids.append(kk)
                    
                    
                template_rec = self.env.ref('partner_statement.email_template_outstanding_statement_ap')
                body = template_rec._render_field(
                    'body_html',
                    [partner.id],
                    
                    compute_lang=False,
                    post_process=True)[partner.id]
                print(222222222222222222222222222,body)
                # template_rec.attachment_ids = [(6, 0, attachment_ids)]
                # template_rec.send_mail(self.id,email_values={'email_to': partner.email})
                
                
                
                if attachment_ids:
#                     values['attachment_ids'] = [(6, 0, attachment_ids)]

                    mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
                mail.write({'attachment_ids': [(6, 0, attachment_ids)]})


                body_html = body

                mail.write({'body_html': body_html,
                            'subject' : template_rec.subject,
                            'recipient_ids':recipient_ids})
                mail.send()
                attachments = False
                template = False
                report_name = False
                report = False
                result = False
                attachment_ids = False
