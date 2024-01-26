from odoo.http import Controller
from ..helpers import ApiException


class Product(Controller):

    def get_categories(self, cr, env, params):
        try:
            data = []
            categories = env['product.category'].sudo().search([], order='id')
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            for item in categories:
                image_url = f'{base_url}/web/image2/product.category/{item.id}/image'
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'image': image_url,
                    'description': item.description,
                })

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_products(self, cr, env, params):
        try:
            data = []
            category_id = params.get('category_id')
            min = params.get('min')
            max = params.get('max')
            order = params.get('order')
            page = params.get('page', 1)
            items_per_page = params.get('items_per_page', 10)
            domain = [('category_id', '=', category_id)]
            order_condition = 'id asc'

            if (min == 0 and max == 100000) or (not min and not max):
                pass
            else:
                domain += [('price', '>=', min), ('price', '<=', max)]
            if order and order != 'default':
                order_condition = order.split('_')[0] + ' ' + order.split('_')[1]
            products = env['kct.product'].sudo().search(domain, order=order_condition)
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            for item in products:
                image_url = f'{base_url}/web/image2/kct.product/{item.id}/image'
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'image': image_url,
                    'price': item.price,
                })

            data = data[page * items_per_page - items_per_page:page * items_per_page]
            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_product_detail(self, cr, env, params):
        try:
            product_id = params.get('product_id')
            product = env['kct.product'].sudo().search([('id', '=', product_id)])
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            image_url = f'{base_url}/web/image2/kct.product/{product.id}/image'
            data = {
                'id': product.id,
                'name': product.name,
                'image': image_url,
                'description': product.description,
                'price': product.price,
                'has_sugar': product.has_sugar,
                'has_ice': product.has_ice,
                'size_ids': [{
                    'id': item.id,
                    'title': item.name,
                    'price': item.price,
                } for item in product.size_ids],
                'topping_ids': [{
                    'id': item.id,
                    'title': item.name,
                    'price': item.price,
                } for item in product.topping_ids],
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
