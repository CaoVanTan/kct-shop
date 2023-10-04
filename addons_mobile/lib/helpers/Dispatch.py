# -*- coding: utf-8 -*-
import json
import traceback
import jwt
from odoo import _, SUPERUSER_ID, api, tools, registry
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

        def save_log(user, params, exception, exception_message, exception_data):
            _regis = registry(db_name)
            with _regis.cursor() as _cr:
                _env = api.Environment(_cr, SUPERUSER_ID, context)
                _uid = user.id if user else user
                _env['api.logger'].create({'name': '%s|%s' % (str(ins), action),
                                           'user_id': _uid,
                                           'params': params,
                                           'exception': exception,
                                           'exception_message': exception_message,
                                           'exception_data': exception_data})

        # Cập nhật cho trường hợp sử dụng jsonrpc để lấy dữ liệu
        data = dict(request.params) if request.httprequest.method == 'GET' else request.httprequest.data
        params = json.loads(data)
        if params.get('jsonrpc', False):
            params = params.get('params', {})
        params.update(additional_params)

        dispatch = getattr(ins, action)
        if not dispatch:
            raise ApiException(_('Action has not been defined.'), ApiException.METHOD_NOT_FOUND)

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
            elif params.get('type') in ['facebook', 'google', 'apple']:
                env, user = Dispatch.social_network_authenticate(params)
            elif params.get('login', False):
                env, user = Dispatch.login_password_authenticate(db_name, params, context)
            elif auth == 'public':
                pass
            else:
                raise ApiException(_('Authentication required.'), ApiException.ACCESS_DENIED)
            lang = context.get('lang', env.lang)
            env = env(context={'lang': lang})
        params['user_type'] = Dispatch.__get_user_type(user)
        Params.verify(verify, params)
        try:
            return dispatch(request.cr, env, params)
        except ApiException as e:
            if env:
                env.cr.rollback()
            save_log(user, params, 'ApiException', str(e), traceback.format_exc())
            raise e
        except AccessError as e:
            save_log(user, params, 'AccessError', str(e), traceback.format_exc())
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except MissingError as e:
            save_log(user, params, 'MissingError', str(e), traceback.format_exc())
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except UserError as e:
            save_log(user, params, 'UserError', str(e), traceback.format_exc())
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except ValidationError as e:
            save_log(user, params, 'ValidationError', str(e), traceback.format_exc())
            raise ApiException(e.name, ApiException.UNKNOWN_ERROR)
        except except_orm as e:
            save_log(user, params, 'except_orm', str(e), traceback.format_exc())
            raise ApiException(e.value, ApiException.UNKNOWN_ERROR)
        except IntegrityError as e:
            if e.pgcode == '23505':
                save_log(user, params, 'IntegrityError', str(e), traceback.format_exc())
                raise ApiException(_('A record already exists, please check it again.'), ApiException.UNKNOWN_ERROR)
            save_log(user, params, 'IntegrityError', str(e), traceback.format_exc())
            raise ApiException(_('The system is experiencing problems, please try again later.'),
                               ApiException.UNKNOWN_ERROR)
        except AccessDenied as e:
            save_log(user, params, 'AccessDenied', str(e), traceback.format_exc())
            raise ApiException(_('You do not have access to current data.'), ApiException.ACCESS_DENIED)
        except Exception as e:
            save_log(user, params, 'Exception', str(e), traceback.format_exc())
            raise ApiException(_(str(e)),
                               ApiException.UNKNOWN_ERROR)

    @staticmethod
    def access_token_authenticate(env, params, context):
        Params.verify(['access_token|require|str'], params)

        data = Authentication.verify_access_token(env, params['access_token'])
        login = data.get('login')
        user = env['res.users'].search([('login', '=', login)])
        if Authentication.is_portal(user):
            params['user_type'] = 'portal'
        elif Authentication.is_public(user):
            params['user_type'] = 'public'
        elif Authentication.is_user(user):
            params['user_type'] = 'internal'
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
            if Authentication.is_portal(user):
                params['user_type'] = 'portal'
            elif Authentication.is_public(user):
                params['user_type'] = 'public'
            elif Authentication.is_user(user):
                params['user_type'] = 'interval'
            return env, user
        except ApiException as e:
            raise e
        except Exception as e:
            raise ApiException('Tài khoản hoặc mật khẩu không đúng, vui lòng thử lại.', ApiException.AUTHORIZED)

    @staticmethod
    def __get_user_type(user):
        if not user:
            return ''
        if Authentication.is_portal(user):
            return 'portal'
        elif Authentication.is_public(user):
            return 'public'
        elif Authentication.is_user(user):
            return 'internal'
        return ''

    @staticmethod
    def social_network_authenticate(params):
        try:
            if params.get('type') not in ['facebook', 'google', 'apple']:
                raise ApiException("Hệ thống chưa hỗ trợ đăng nhập với ứng dụng này !")
            Params.verify([
                'accessToken|str|require:type{"facebook","google","apple"}',
            ], params)
            oauth_provider_id = {
                "facebook": 2,
                "google": 3,
                "apple": 4,
            }
            access_token = params.get('accessToken')
            params.update({
                'access_token': access_token,
                'state': "{}",
            })
            if params.get('type') in ['facebook', 'google']:
                validation = request.env(user=SUPERUSER_ID)['res.users'].sudo()._auth_oauth_validate(
                    oauth_provider_id[params.get('type')], access_token)
                params.update({
                    'login': validation.get('email')
                })
                user = request.env(user=SUPERUSER_ID)['res.users'].search([('login', '=', params.get('login')),
                                                                           ('oauth_provider_id', '!=',
                                                                            oauth_provider_id[params.get('type')])])
                if user:
                    raise ApiException(
                        _("Một tài khoản khác đã được đăng ký với địa chỉ email này."),
                        ApiException.AUTHORIZED)

                db_name, login, access_token = request.env(user=SUPERUSER_ID)['res.users'].sudo().auth_oauth(
                    oauth_provider_id[params.get('type')], params)
            elif params.get('type') == 'apple':
                data = jwt.decode(params.get('access_token'), verify=False)
                email = data['email']
                user = request.env(user=SUPERUSER_ID)['res.users'].search([('login', '=', email),
                                                                           ('oauth_provider_id', '!=',
                                                                            oauth_provider_id[params.get('type')])])
                if user:
                    raise ApiException(
                        _("Một tài khoản khác đã được đăng ký với địa chỉ email này."),
                        ApiException.AUTHORIZED)
                at_pos = email.find('@')
                name = email[0:at_pos]
                validation = {
                    'user_id': data['sub'],
                    'email': email,
                    'name': name,
                }
                login = request.env(user=SUPERUSER_ID)['res.users'].sudo()._auth_oauth_signin(
                    oauth_provider_id[params.get('type')], validation, params)
                if not login:
                    raise AccessDenied()

            user = request.env(user=SUPERUSER_ID)['res.users'].search([('login', '=', login)])
            env = request.env(user=user.id, context={'lang': user.lang})
            user = env['res.users'].browse(user.id)
            if Authentication.is_portal(user):
                params['user_type'] = 'portal'
            elif Authentication.is_public(user):
                params['user_type'] = 'public'
            elif Authentication.is_user(user):
                params['user_type'] = 'internal'
            params.pop('access_token')
            params.update({
                'login': login
            })
            return env, user
        except ApiException as e:
            raise e
        except Exception as e:
            raise ApiException('Không thể đăng nhập bằng tài khoản này, vui lòng thử lại.', ApiException.AUTHORIZED)

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
