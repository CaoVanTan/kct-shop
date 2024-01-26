from odoo.http import route, Controller
from ..helpers import Route, Dispatch, Response, ApiException
from odoo.addons.api_repository.controllers.base.change_password import \
    ChangePassword as ChangePasswordRespository


class ChangePassword(Controller):

    @route(route=Route('change_password'), method=['POST'], auth='public', type='json')
    def change_password(self):
        verify = [
            'access_token|str|require',
            'old_password:Mật khẩu cũ|str|require',
            'new_password:Mật khẩu mới|str|require',
        ]
        try:
            res = Dispatch.dispatch(ChangePasswordRespository(), 'change_password', verify=verify, auth='public')
            return Response.success('Đổi mật khẩu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
