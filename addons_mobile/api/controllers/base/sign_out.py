from odoo.http import route, Controller
from ..helpers import Route, Dispatch, Response, ApiException
from odoo.addons.api_repository.controllers.base.sign_out import SignOut as SignOutRepository


class SignOut(Controller):

    @route(route=Route('sign_out'), method=['POST'], auth='public', type='json')
    def sign_out(self):
        try:
            Dispatch.dispatch(SignOutRepository(), 'sign_out')
            return Response.success('Đăng xuất thành công', {}).to_json()
        except ApiException as e:
            return e.to_json()
