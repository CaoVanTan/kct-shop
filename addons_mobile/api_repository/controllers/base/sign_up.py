# -*- coding: utf-8 -*-

from odoo.http import Controller, request
from odoo import _
from ..helpers import ApiException, Dispatch
from .sign_in import SignIn


class SignUp(Controller):

    def sign_up(self, cr, env, params):
        """
        Đăng ký tại khoản người dùng

        @param params:
            @requires:  name        |   str |   Họ và tên
                        type        |   str |
                        phone       |   str |   Số điện thoại
                        password    |   str |   Mật khẩu
            @options:
        @return:
        """
        if 'phone' in params:
            params['login'] = params['phone']
        else:
            raise ApiException(_("Vui lòng nhập số điện thoại"), ApiException.PARAM_NOT_PROVIDE)
        if params['type'] == "odoo":
            values = {key: params.get(key) for key in ('login', 'name', 'password')}

            if env["res.users"].sudo().search([("login", "=", params.get("login"))]):
                raise ApiException(_('Một tài khoản khác đã được đăng ký với số điện thoại này.'),
                                   ApiException.AUTHORIZED)

            supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
            lang = request.context.get('lang', '').split('_')[0]
            if lang in supported_lang_codes:
                values['lang'] = lang

            request.env['res.users'].sudo().signup(values, token=None)
            request.env.cr.commit()

        return True
