from odoo.http import Controller
from ..helpers import ApiException


class AccountProduct(Controller):
    def get_products(self, cr, env, params):
        try:
            data = []
            categories = env['product.category'].search([])

            for item in categories:
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'complete_name': item.complete_name,
                })

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
