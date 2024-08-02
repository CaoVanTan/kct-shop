from odoo.http import Controller
from ..helpers import ApiException
from ..base.ir_http import IrHttp

import base64



class Product(Controller):

    def get_categories(self, cr, env, params):
        try:
            data = []
            keyword = params.get('keyword')
            page = params.get('page', 1)
            items_per_page = params.get('items_per_page', 100)

            domain_search = []
            if keyword:
                domain_search += [('name', 'ilike', keyword)]
            categories = env['product.category'].sudo().search(domain_search, order='id')
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            for item in categories:
                image_url = f'{base_url}/web/image2/product.category/{item.id}/image'
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'image': image_url,
                    'description': item.description or '',
                })
            data = data[page * items_per_page - items_per_page:page * items_per_page]
            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_category_detail(self, cr, env, params):
        try:
            id = params.get('id')
            category = env['product.category'].sudo().search([('id', '=', id)])
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            image_url = f'{base_url}/web/image2/product.category/{category.id}/image'
            data = {
                'id': category.id,
                'name': category.name,
                'description': category.description or '',
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def create_category(self, cr, env, params):
        try:
            name = params.get('name')
            description = params.get('description')

            vals = {
                'name': name,
                'description': description,
            }
            category = env['product.category'].sudo().create(vals)

            return {'id': category.id, 'name': category.name}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def update_category(self, cr, env, params):
        try:
            id = params.get('id')
            name = params.get('name')
            description = params.get('description')

            category = env['product.category'].sudo().search([('id', '=', id)], limit=1)
            if not category:
                raise ApiException('Danh mục sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)

            vals = {
                'name': name,
                'description': description,
            }
            category.sudo().write(vals)

            return {'id': category.id, 'name': category.name}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def delete_category(self, cr, env, params):
        try:
            id = params.get('id')

            category = env['product.category'].sudo().search([('id', '=', id)], limit=1)
            if not category:
                raise ApiException('Danh mục sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)
            category.unlink()

            return {'id': category.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    # def get_products(self, cr, env, params):
    #     try:
    #         data = []
    #         category_id = params.get('category_id')
    #         min = params.get('min')
    #         max = params.get('max')
    #         order = params.get('order')
    #         page = params.get('page', 1)
    #         items_per_page = params.get('items_per_page', 10)
    #         domain = [('category_id', '=', category_id)]
    #         order_condition = 'id asc'
    #
    #         if (min == 0 and max == 100000) or (not min and not max):
    #             pass
    #         else:
    #             domain += [('price', '>=', min), ('price', '<=', max)]
    #         if order and order != 'default':
    #             order_condition = order.split('_')[0] + ' ' + order.split('_')[1]
    #         products = env['kct.product'].sudo().search(domain, order=order_condition)
    #         base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'
    #
    #         for item in products:
    #             image_url = f'{base_url}/web/image2/kct.product/{item.id}/image'
    #             data.append({
    #                 'id': item.id,
    #                 'name': item.name,
    #                 'description': item.description,
    #                 'image': image_url,
    #                 'price': item.price,
    #             })
    #
    #         data = data[page * items_per_page - items_per_page:page * items_per_page]
    #         return data
    #     except Exception as e:
    #         return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    # def get_product_detail(self, cr, env, params):
    #     try:
    #         product_id = params.get('id')
    #         product = env['kct.product'].sudo().search([('id', '=', product_id)])
    #         base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'
    #
    #         image_url = f'{base_url}/web/image2/kct.product/{product.id}/image'
    #         data = {
    #             'id': product.id,
    #             'name': product.name,
    #             'image': image_url,
    #             'description': product.description,
    #             'price': product.price,
    #             'has_sugar': product.has_sugar,
    #             'has_ice': product.has_ice,
    #             'size_ids': [{
    #                 'id': item.id,
    #                 'title': item.name,
    #                 'price': item.price,
    #             } for item in product.size_ids],
    #             'topping_ids': [{
    #                 'id': item.id,
    #                 'title': item.name,
    #                 'price': item.price,
    #             } for item in product.topping_ids],
    #         }
    #
    #         return data
    #     except Exception as e:
    #         return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_products(self, cr, env, params):
        try:
            data = []
            keyword = params.get('keyword')
            page = params.get('page', 1)
            items_per_page = params.get('items_per_page', 100)

            domain_search = []
            if keyword:
                domain_search += ['|', ('name', 'ilike', keyword), ('default_code', 'ilike', keyword)]

            products = env['product.template'].sudo().search(domain_search)
            for item in products:
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'code': item.default_code,
                    'description': item.description_sale or '',
                    'image': IrHttp.get_image(self, env, model='product.template', model_id=item.id, field="image_1920"),
                    'price': item.list_price,
                    'category_id': {
                        'id': item.categ_id.id,
                        'name': item.categ_id.name,
                        'description': item.categ_id.description,
                    },
                })

            data = data[page * items_per_page - items_per_page:page * items_per_page]
            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_product_detail(self, cr, env, params):
        try:
            id = params.get('id')

            product = env['product.template'].sudo().search([('id', '=', id)])
            data = {
                'id': product.id,
                'name': product.name,
                'code': product.default_code,
                'image': IrHttp.get_image(self, env, model='product.template', model_id=product.id, field="image_1920"),
                'description': product.description_sale or '',
                'price': product.list_price,
                'category_id': {
                    'id': product.categ_id.id,
                    'name': product.categ_id.name,
                    'description': product.categ_id.description,
                },
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def create_product(self, cr, env, params):
        try:
            name = params.get('name')
            image = params.get('image')
            price = params.get('price')
            code = params.get('code')
            description = params.get('description')
            category_id = params.get('category_id')

            category = env['product.category'].sudo().search([('id', '=', category_id)], limit=1)
            if not category:
                raise ApiException('Danh mục sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)

            vals = {
                'name': name,
                'list_price': price,
                'default_code': code,
                'description_sale': description,
                'categ_id': category.id,
            }
            if image:
                vals['image_1920'] = image
            product = env['product.template'].sudo().create(vals)

            return {'id': product.id, 'name': product.name}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def update_product(self, cr, env, params):
        try:
            id = params.get('id')
            name = params.get('name')
            image = params.get('image')
            price = params.get('price')
            code = params.get('code')
            description = params.get('description')
            category_id = params.get('category_id')

            product = env['product.template'].sudo().search([('id', '=', id)], limit=1)
            if not product:
                raise ApiException('Sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)

            category = env['product.category'].sudo().search([('id', '=', category_id)], limit=1)
            if not category:
                raise ApiException('Danh mục sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)

            vals = {
                'name': name,
                'list_price': price,
                'default_code': code,
                'description_sale': description,
                'categ_id': category.id,
            }
            if image:
                vals['image_1920'] = base64.b64decode(image)

            product.sudo().write(vals)

            return {'id': product.id, 'name': product.name}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def delete_product(self, cr, env, params):
        try:
            id = params.get('id')

            product = env['product.template'].sudo().search([('id', '=', id)], limit=1)
            if not product:
                raise ApiException('Sản phẩm không tồn tại!', ApiException.UNKNOWN_ERROR)
            product.unlink()

            return {'id': product.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)