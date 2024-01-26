from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    device_ids = fields.One2many('res.users.device', 'user_id', string='Access device')

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
