from odoo.http import Controller
from ..helpers import ApiException
from odoo.exceptions import UserError, AccessDenied


class ChangePassword(Controller):

    def change_password(self, cr, env, params):

        if params.get('old_password', '') == '':
            raise ApiException('Vui lòng nhập mật khẩu cũ!!!', ApiException.PARAM_NOT_PROVIDE)
        if params.get('new_password', '') == '':
            raise ApiException('Vui lòng nhập mật khẩu mới!!!', ApiException.PARAM_NOT_PROVIDE)
        old_password = params.get('old_password')
        new_password = params.get('new_password')
        try:
            result = env['res.users'].change_password(old_password, new_password)
        except AccessDenied as e:
            raise ApiException('Mật khẩu cũ không chính xác', ApiException.ACCESS_DENIED)
        except UserError as e:
            raise ApiException(f'{e.name}', ApiException.UNKNOWN_ERROR)
        return result
