from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.profile.profile import \
    Profile as ProfileRepository


class Profile(Controller):

    @route(route=Route('profile/edit'), method=['POST'], auth='public', type='json')
    def edit_profile(self):
        verify = [
            'access_token|str|require',
            'name|str|require',
            'phone|str:0{1}[0-9]{9}|require',
        ]
        try:
            res = Dispatch.dispatch(ProfileRepository(), 'edit_profile', verify=verify, auth=True)
            return Response.success('Sửa thông tin thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
