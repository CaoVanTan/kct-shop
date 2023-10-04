from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.account_product.account_product import \
    AccountProduct as AccountProductRepository


class AccountProduct(Controller):

    @route(route=Route('get_products'), method=['POST'], auth='public', type='json')
    def get_products(self):
        verify = [
            'access_token|str|require',
            'category_id|int|require',
        ]
        try:
            res = Dispatch.dispatch(AccountProductRepository(), 'get_products', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
