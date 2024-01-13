from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.notification.notification import \
    Notification as NotificationRepository


class Notification(Controller):

    @route(route=Route('get_notifications'), method=['POST'], auth='public', type='json')
    def get_address(self):
        verify = [
            'access_token|str|require',
            'device_id|str|require',
        ]
        try:
            res = Dispatch.dispatch(NotificationRepository(), 'get_notifications', verify=verify, auth=True)
            return Response.success('Lấy thông tin thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
