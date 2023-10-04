from odoo.http import Controller
from ..helpers import ApiException


class AccountCategory(Controller):
    def get_categories(self, cr, env, params):
        try:
            data = []
            categories = env['product.category'].search([], order='id')

            for item in categories:
                data.append({
                    'id': item.id,
                    'name': item.name,
                })

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
