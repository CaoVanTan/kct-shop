# -*- coding: utf-8 -*-
import jwt
from .ApiException import ApiException
from datetime import datetime


class Authentication(object):
    __KEY = 'i3jn43gd5kj98e0'

    @staticmethod
    def generate_access_token(login, device_id):
        payload = {'login': login,
                   'device_id': device_id,
                   'ts': datetime.now().timestamp()}
        return jwt.encode(payload, Authentication.__KEY, algorithm='HS256')

    @staticmethod
    def verify_access_token(env, access_token):
        try:
            data = jwt.decode(access_token, Authentication.__KEY, algorithms=['HS256'])
            header, payload, sign = access_token.split('.')
            is_sign_in = env['res.users.device'].search([('access_token', '=', sign)])
            if not is_sign_in:
                raise Exception()

            return data
        except Exception as e:
            raise ApiException('Access token không hợp lệ', ApiException.INVALID_ACCESS_TOKEN)
