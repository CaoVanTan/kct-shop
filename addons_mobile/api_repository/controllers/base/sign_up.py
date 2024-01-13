# -*- coding: utf-8 -*-

from odoo.http import Controller, request
from ..helpers import ApiException

class SignUp(Controller):

    def sign_up(self, cr, env, params):
        if 'email' in params:
            params['login'] = params['email']
            values = {key: params.get(key) for key in ('login', 'name', 'phone', 'password')}
            if env["res.users"].sudo().search([("login", "=", params.get("login"))]):
                raise ApiException('Một tài khoản khác đã được đăng ký với email này.', ApiException.AUTHORIZED)

            supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
            lang = request.context.get('lang', '').split('_')[0]
            if lang in supported_lang_codes:
                values['lang'] = lang

            request.env['res.users'].sudo().signup(values, token=None)
            request.env.cr.commit()
            return True
        else:
            raise ApiException("Vui lòng nhập email", ApiException.PARAM_NOT_PROVIDE)
