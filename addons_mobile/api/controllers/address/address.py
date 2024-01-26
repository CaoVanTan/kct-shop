from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.address.address import \
    Address as AddressRepository


class Address(Controller):

    @route(route=Route('get_address'), method=['POST'], auth='public', type='json')
    def get_address(self):
        verify = [
            'access_token|str|require',
        ]
        try:
            res = Dispatch.dispatch(AddressRepository(), 'get_address', verify=verify, auth=True)
            return Response.success('Lấy thông tin thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('address/create'), method=['POST'], auth='public', type='json')
    def create_address(self):
        verify = [
            'access_token|str|require',
            'address|str|require',
            'address_detail|str|require',
            'label|str|require',
            'lat|float|require',
            'long|float|require',
        ]
        try:
            res = Dispatch.dispatch(AddressRepository(), 'create_address', verify=verify, auth=True)
            return Response.success('Tạo bản ghi thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('address/edit'), method=['POST'], auth='public', type='json')
    def edit_address(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
            'address|str',
            'address_detail|str',
            'label|str',
            'lat|float',
            'long|float',
            'selected|bool',
        ]
        try:
            res = Dispatch.dispatch(AddressRepository(), 'edit_address', verify=verify, auth=True)
            return Response.success('Sửa thông tin thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('address/delete'), method=['POST'], auth='public', type='json')
    def delete_address(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(AddressRepository(), 'delete_address', verify=verify, auth=True)
            return Response.success('Xóa bản ghi thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
