from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.order.order import \
    Order as OrderRepository


class Order(Controller):

    @route(route=Route('get_orders'), method=['POST'], auth='public', type='json')
    def get_orders(self):
        verify = ['access_token|str|require']
        try:
            res = Dispatch.dispatch(OrderRepository(), 'get_orders', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_order_detail'), method=['POST'], auth='public', type='json')
    def get_order_detail(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'get_order_detail', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('sale_order/create'), method=['POST'], auth='public', type='json')
    def create_sale_order(self):
        verify = [
            'access_token|str|require',
            'product_ids|list|require',
            'address_id|int|require',
            'payment_method|str|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'create_sale_order', verify=verify, auth=True)
            return Response.success('Tạo đơn hàng thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('sale_order/cancel'), method=['POST'], auth='public', type='json')
    def cancel_sale_order(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'cancel_sale_order', verify=verify, auth=True)
            return Response.success('Hủy đơn hàng thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_orders_employee'), method=['POST'], auth='public', type='json')
    def get_orders_employee(self):
        verify = [
            'access_token|str|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'get_orders_employee', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('get_order_detail_employee'), method=['POST'], auth='public', type='json')
    def get_order_detail_employee(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'get_order_detail_employee', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('sale_order/update'), method=['POST'], auth='public', type='json')
    def update_sale_order(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
            'action|str|require',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'update_sale_order', verify=verify, auth=True)
            return Response.success('Cập nhật dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()

    @route(route=Route('rating_sale_order'), method=['POST'], auth='public', type='json')
    def rating_sale_order(self):
        verify = [
            'access_token|str|require',
            'id|int|require',
            'rating_emp|str|require',
            'rating_product|str|require',
            'rating_detail|str',
        ]
        try:
            res = Dispatch.dispatch(OrderRepository(), 'rating_sale_order', verify=verify, auth=True)
            return Response.success('Cập nhật dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()