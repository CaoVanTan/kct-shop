from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.product.product import \
    Product as ProductRepository


class Product(Controller):

    @route(route=Route('get_categories'), method=['POST'], auth='public', type='json')
    def get_categories(self):
        verify = []
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_categories', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    # @route(route=Route('get_products'), method=['POST'], auth='public', type='json')
    # def get_products(self):
    #     verify = [
    #         'category_id|int|require',
    #         'filter|dict',
    #         'order|str',
    #         'page|int',
    #         'items_per_page|int',
    #     ]
    #     try:
    #         res = Dispatch.dispatch(ProductRepository(), 'get_products', verify=verify, auth=False)
    #         return Response.success('Lấy dữ liệu thành công', data=res).to_json()
    #     except ApiException as e:
    #         return e.to_json()
    @route(route=Route('get_products'), method=['POST'], auth='public', type='json')
    def get_products(self):
        verify = [
            'page|int',
            'items_per_page|int',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_products', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_product_detail'), method=['POST'], auth='public', type='json')
    def get_product_detail(self):
        verify = [
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_product_detail', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('product/create'), method=['POST'], auth='public', type='json')
    def create_product(self):
        verify = [
            'access_token|str|require',
            'name|str|require',
            'image|str',
            'price|double|require',
            'code|str|require',
            'description|str',
            'category_id|int|require',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'create_product', verify=verify, auth=True)
            return Response.success('Tạo bản ghi thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('product/update'), method=['POST'], auth='public', type='json')
    def update_product(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
            'name|str|require',
            'image|str',
            'price|double|require',
            'code|str|require',
            'description|str',
            'category_id|int|require',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'update_product', verify=verify, auth=True)
            return Response.success('Cập nhật bản ghi thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('product/delete'), method=['POST'], auth='public', type='json')
    def delete_product(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'delete_product', verify=verify, auth=True)
            return Response.success('Xóa bản ghi thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
