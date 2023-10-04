from odoo.http import route, Controller
from ..helpers import Route, Dispatch, ApiException, Response
from odoo.addons.api_repository.controllers.account_product.account_category import \
    AccountCategory as AccountCategoryRepository


class AccountCategory(Controller):

    @route(route=Route('get_categories'), method=['POST'], auth='public', type='json')
    def get_categories(self):
        verify = ['access_token|str|require']
        try:
            res = Dispatch.dispatch(AccountCategoryRepository(), 'get_categories', verify=verify, auth=True)
            return Response.success('Lấy dữ liệu thành công', data=res).to_json()
        except ApiException as e:
            return e.to_json()
