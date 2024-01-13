# -*- coding: utf-8 -*-

from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.base.sign_in import SignIn as SignInRepository


class SignIn(Controller):

    @route(route=Route('sign_in'), method=['POST'], auth='public', type='json')
    def sign_in(self):
        verify = ['login|str|require:type{"odoo"}',
                  'password|str|require:type{"odoo"}',
                  'device_id|str|require',
                  'device_info|str',
                  'firebase_token|str',
                  'role|str|require',
                  ]
        try:
            res = Dispatch.dispatch(SignInRepository(), 'sign_in', verify=verify, auth=True)
            return Response.success('Đăng nhập thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
