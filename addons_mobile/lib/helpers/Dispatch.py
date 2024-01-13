# -*- coding: utf-8 -*-
import json
from odoo import SUPERUSER_ID, tools
from odoo.http import request
from odoo.exceptions import except_orm, AccessError, ValidationError, MissingError, UserError, AccessDenied
from psycopg2 import IntegrityError
from .ApiException import ApiException
from .Params import Params
from .Authentication import Authentication


class Dispatch(object):
    @staticmethod
    def dispatch(ins, action: str, verify: list = [], auth: any = True, additional_params: dict = {}):
        """
        Hàm làm nhiệm vụ, kiểm tra thông tin dữ liệu, điều hướng thực thi tác vụ

        @param ins:                 Đối tượng chứa action
        @param action:              Hàm được điều hướng
        @param verify:              Quy tắc kiểm tra dữ liệu
        @param auth:                Xác thực người dùng thông qua access_token
        @param additional_params:   Tham số bổ sung sau khi sử lý dữ liệu trên router và muốn gọi đến 1 controller khác
        @return:                    Trả về dữ liệu được trả về từ action
        """

        # Cập nhật cho trường hợp sử dụng jsonrpc để lấy dữ liệu
        data = dict(request.params) if request.httprequest.method == 'GET' else request.httprequest.data
        params = json.loads(data)
        if params.get('jsonrpc', False):
            params = params.get('params', {})
        params.update(additional_params)

        dispatch = getattr(ins, action)
        if not dispatch:
            raise ApiException('Action has not been defined.', ApiException.METHOD_NOT_FOUND)

        db_name = Dispatch.__get_db_name()
        context = request.context
        if params.get('lang'):
            context = dict(context)
            context['lang'] = params.get('lang')
        env = request.env(user=SUPERUSER_ID, context=context)
        user = False

        if auth:
            if params.get('access_token', False):
                env, user = Dispatch.access_token_authenticate(env, params, context)
            elif request.session.uid:
                env = request.env(user=request.session.uid)
                user = env['res.users'].browse(request.session.uid)
            elif params.get('login', False):
                env, user = Dispatch.login_password_authenticate(db_name, params, context)
            else:
                raise ApiException('Authentication required.', ApiException.ACCESS_DENIED)
            env = env(context={'lang': user.lang})

        if verify:
            Params.verify(verify, params)

        try:
            return dispatch(request.cr, env, params)
        except ApiException as e:
            if env:
                env.cr.rollback()
            raise e
        except AccessError as e:
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except MissingError as e:
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except UserError as e:
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except ValidationError as e:
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except except_orm as e:
            raise ApiException(e.value, ApiException.UNKNOWN_ERROR)
        except IntegrityError as e:
            if e.pgcode == '23505':
                raise ApiException('A record already exists, please check it again.', ApiException.UNKNOWN_ERROR)
            raise ApiException('The system is experiencing problems, please try again later.',
                               ApiException.UNKNOWN_ERROR)
        except AccessDenied as e:
            raise ApiException('You do not have access to current data.', ApiException.ACCESS_DENIED)
        except Exception as e:
            raise ApiException(str(e), ApiException.UNKNOWN_ERROR)

    @staticmethod
    def access_token_authenticate(env, params, context):
        Params.verify(['access_token|require|str'], params)

        data = Authentication.verify_access_token(env, params['access_token'])
        login = data.get('login')
        user = env['res.users'].search([('login', '=', login)])
        env = request.env(user=user.id)
        Dispatch.validate_access_token_expired(user, params['access_token'])
        return env, user

    @staticmethod
    def login_password_authenticate(db_name, params, context):
        try:
            Params.verify(['login|str|require', 'password|str|require'], params)
            uid = request.env['res.users'].authenticate(db_name, params['login'], params['password'], {})
            env = request.env(user=uid, context=context)
            user = env['res.users'].browse(uid)
            return env, user
        except ApiException as e:
            raise e
        except Exception as e:
            raise ApiException('Tài khoản hoặc mật khẩu không đúng, vui lòng thử lại.', ApiException.AUTHORIZED)

    @staticmethod
    def validate_access_token_expired(user, access_token):
        if user.is_access_token_expired(access_token):
            raise ApiException('Cảnh báo', 'Access token đã hết hạn, vui lòng đăng nhập lại')
        user.reset_access_token_expire(access_token)

    @staticmethod
    def __get_db_name():
        if tools.config.options.get('db_name'):
            return tools.config.options.get('db_name')
        return tools.config.options.get('dbfilter')
