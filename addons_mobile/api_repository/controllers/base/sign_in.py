# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.http import Controller
from odoo import _
from ..helpers import Authentication, ApiException
import logging

_logger = logging.getLogger(__name__)


class SignIn(Controller):

    def sign_in(self, cr, env, params):
        """
        Đăng nhập hệ thống

        @param params: Danh sách tham số gửi lên từ client
            @requires:  login           | str   |   email
                        password        | str   |   mật khẩu
                        device_id       | str   |   id thiết bị đăng nhập
            @options:   device_info     | str   |   Thông tin thiết bị đăng nhập
                        firebase_token  | str   |   Firebase token
        @return: Trả về thông tin user đăng nhập
        """

        access_token = Authentication.generate_access_token(params['login'], params['device_id'])
        header, payload, sign = access_token.split('.')

        user = env['res.users'].search([('login', '=', params['login'])])
        if not user:
            raise ApiException(_('Tài khoản hoặc mật khẩu không hợp lệ'), ApiException.UNKNOWN_ERROR)

        UserDevice = env['res.users.device']

        check_exist_login = UserDevice.search([('access_token', '=', sign)])
        if check_exist_login:
            check_exist_login.write({'firebase_token': params.get('firebase_token', '')})
        else:
            UserDevice.create({'user_id': user.id,
                               'device_id': params.get('device_id'),
                               'device_info': params.get('device_info', ''),
                               'access_token': sign,
                               'firebase_token': params.get('firebase_token', '')})

        data = {}
        try:
            if user.has_group('base.group_user'):
                data = self.__get_internal_user_data(env, user, access_token)
            return data
        except Exception as e:
            raise ApiException(str(e), ApiException.UNKNOWN_ERROR)

    @staticmethod
    def __get_internal_user_data(env, user, access_token):
        roles = Authentication.get_user_roles(user)
        employee = env['hr.employee'].search([('user_id', '=', user.id)])
        data = {
            'user_type': 'internal',
            'access_token': access_token,
            'user_id': {'id': user.id,
                        'name': user.name or '',
                        'email': user.login or '',
                        'img_url': env['ir.config_parameter'].sudo().get_param(
                            'web.base.url') + f'/web/image/user/{user.id}?timestamp={int(datetime.now().timestamp())}',
                        },
            'partner_id': {'id': user.partner_id.id,
                           'name': user.partner_id.name or ''},
            'company_id': {'id': user.company_id.id,
                           'name': user.company_id.name or ''},
            'department_id': {'id': employee.department_id.id,
                              'name': employee.department_id.name or ''},
            'employee_id': {'id': employee.id or False,
                            'name': employee.name or '',
                            'img_url': env['ir.config_parameter'].sudo().get_param(
                                'web.base.url') + f'/web/image/employee/{employee.id}?timestamp={int(datetime.now().timestamp())}',
                            },
            'roles': roles,
        }
        return data
