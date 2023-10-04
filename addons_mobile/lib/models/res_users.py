# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.addons.auth_signup.models.res_partner import now

from odoo.exceptions import UserError
import logging as _logger


class ResUsers(models.Model):
    _inherit = 'res.users'

    device_ids = fields.One2many('res.users.device', 'user_id', string='Access device')
    change_user_password = fields.Boolean(string='Change User Password', default=False)

    def website_visitor_synch(self, device_id, sign):
        """ Override to link the logged in user's res.partner to website.visitor """
        visitor_sudo = self.env['website.visitor']._get_visitor_from_request_app(device_id)
        if visitor_sudo:
            partner = self.env.user.partner_id
            partner_visitor = self.env['website.visitor'].with_context(active_test=False).sudo().search(
                [('partner_id', '=', partner.id)])
            if partner_visitor and partner_visitor.id != visitor_sudo.id:
                # Link history to older Visitor and delete the newest
                visitor_sudo.website_track_ids.write({'visitor_id': partner_visitor.id})
                visitor_sudo.unlink()
                # If archived (most likely by the cron for inactivity reasons), reactivate the partner's visitor
                if not partner_visitor.active:
                    partner_visitor.write({'active': True})
            else:
                vals = {
                    'partner_id': partner.id,
                    'name': partner.name,
                    'access_token': sign
                }
                visitor_sudo.write(vals)

    def is_access_token_expired(self, access_token):
        # Nếu quá hạn trả về True
        sign = access_token.split('.')[2]
        for device in self.device_ids:
            if device.access_token == sign and (not device.expired or device.expired < datetime.now()):
                device.unlink()
                return True
        return False

    def reset_access_token_expire(self, access_token):
        expire = self.get_expired()
        sign = access_token.split('.')[2]
        for device in self.device_ids:
            if device.access_token == sign:
                device.expired = expire
                break

    def get_expired(self):
        return datetime.now() + relativedelta(seconds=int(self.env.ref('lib.access_token_expired').sudo().value))

    @api.model
    def signup(self, values, token=None):
        # Thêm đánh dấu đổi mật khẩu
        values['change_user_password'] = True
        return super(ResUsers, self).signup(values, token)

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_cc': False,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get('import_file', False))
                template.with_context(lang=user.lang).send_mail(user.id, force_send=force_send, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
