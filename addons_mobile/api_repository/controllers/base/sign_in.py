from datetime import datetime
from odoo.http import Controller
from ..helpers import Authentication, ApiException


class SignIn(Controller):

    def sign_in(self, cr, env, params):
        access_token = Authentication.generate_access_token(params['login'], params['device_id'])
        header, payload, sign = access_token.split('.')
        role = params.get('role')

        user = env['res.users'].search([('login', '=', params['login'])])
        if not user or not user.has_group(f'base.{role}'):
            raise ApiException('Tài khoản hoặc mật khẩu không chính xác', ApiException.UNKNOWN_ERROR)

        UserDevice = env['res.users.device']

        check_exist_login = UserDevice.search(
            [('user_id', '=', params['login']), ('device_id', '=', params['device_id'])], order='id desc', limit=1)
        if check_exist_login:
            check_exist_login.write({'access_token': sign, 'firebase_token': params.get('firebase_token', '')})
            user.reset_access_token_expire(access_token)
        else:
            UserDevice.create({
                'user_id': user.id,
                'device_id': params.get('device_id'),
                'device_info': params.get('device_info', ''),
                'access_token': sign,
                'firebase_token': params.get('firebase_token', ''),
            })

        try:
            data = self.__get_user_data(env, user, access_token)
            return data
        except Exception as e:
            raise ApiException(str(e), ApiException.UNKNOWN_ERROR)

    @staticmethod
    def __get_user_data(env, user, access_token):
        data = {
            'access_token': access_token,
            'user_id': {
                'id': user.id,
                'name': user.name or '',
                'email': user.login or '',
                'phone': user.partner_id.phone or '',
                'img_url': env['ir.config_parameter'].sudo().get_param(
                    'web.base.url') + f'/web/image/user/{user.id}?timestamp={int(datetime.now().timestamp())}',
            },
        }
        return data
