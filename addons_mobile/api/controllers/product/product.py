from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.product.product import \
    Product as ProductRepository


class Product(Controller):

    @route(route=Route('get_categories'), method=['POST'], auth='public', type='json')
    def get_categories(self):
        verify = []
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_categories', verify=verify, auth=False)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_products'), method=['POST'], auth='public', type='json')
    def get_products(self):
        verify = [
            'category_id|int|require',
            'filter|dict',
            'order|str',
            'page|int',
            'items_per_page|int',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_products', verify=verify, auth=False)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_product_detail'), method=['POST'], auth='public', type='json')
    def get_product_detail(self):
        verify = [
            'product_id|int|require',
        ]
        try:
            res = Dispatch.dispatch(ProductRepository(), 'get_product_detail', verify=verify, auth=False)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
