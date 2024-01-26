from odoo.http import Controller
from ..helpers import ApiException


class Profile(Controller):

    def edit_profile(self, cr, env, params):
        try:
            name = params.get('name')
            phone = params.get('phone')
            partner_id = env['res.partner'].sudo().browse([env.user.partner_id.id])
            partner_id.write({
                'name': name,
                'phone': phone,
            })
            return {'id': partner_id.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
