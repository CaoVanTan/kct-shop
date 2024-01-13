# -*- coding: utf-8 -*-
from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.base.sign_up import SignUp as SignUpRepository


class SignUp(Controller):

    @route(route=Route('sign_up'), method=['POST'], auth='public', type='json')
    def sign_up(self):
        verify = ['name|str|require',
                  'email|str:[\w\.]+@[\w]+(\.[a-zA-Z]{2,}){1,}|require:type{"odoo"}',
                  'phone|str:0{1}[0-9]{9}|require',
                  'password|str|require:type{"odoo"}',
                  'device_id|str|require',
                  'device_info|str',
                  'firebase_token|str',
                  ]
        try:
            res = Dispatch.dispatch(SignUpRepository(), 'sign_up', verify=verify, auth=False)
            return Response.success('Đăng ký tài khoản thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
