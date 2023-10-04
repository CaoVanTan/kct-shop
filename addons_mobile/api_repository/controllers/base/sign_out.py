# -*- coding: utf-8 -*-

from odoo.http import Controller
from ..helpers import ApiException


class SignOut(Controller):

    def sign_out(self, cr, env, params):
        """
        Đăng xuất

        @param params: Danh sách tham số gửi lên từ client
            @requires:  access_token    | str   | Access token
            @options:
        @return: Trả về true nếu đăng nhập thành công
                        message nếu đăng nhập thất bại
        """
        try:
            header, payload, sign = params.get('access_token').split('.')

            UserDevice = env['res.users.device']

            check_exist_login = UserDevice.search([('access_token', '=', sign)])
            if check_exist_login:
                check_exist_login.unlink()
                return True
            return ApiException('Không thể đăng xuất với access token được cung cấp', ApiException.INVALID_ACCESS_TOKEN)
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
