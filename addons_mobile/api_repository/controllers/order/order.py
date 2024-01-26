from odoo.http import Controller
from ..helpers import ApiException
import pytz


class Order(Controller):

    def get_orders(self, cr, env, params):
        try:
            data = {
                'new': [],
                'history': [],
            }
            order_ids = env['sale.order'].sudo().search([('partner_id', '=', env.user.partner_id.id)], order='id desc')
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            for order in order_ids:
                order_line = env['sale.order.line'].sudo().search([('order_id', '=', order.id)], limit=1)
                image_url = f'{base_url}/web/image2/kct.product/{order_line.x_product_id.id}/image'
                vals = {
                    'id': order.id,
                    'name': order.name,
                    'image': image_url,
                    'state': order.x_state,
                    'amount_total': order.x_amount_total,
                }
                if order.x_state in ['pending', 'received', 'waiting', 'delivering']:
                    data['new'].append(vals)
                elif order.x_state in ['delivered', 'done']:
                    data['history'].append(vals)

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_order_detail(self, cr, env, params):
        try:
            id = params.get('id')
            order_id = env['sale.order'].sudo().search([('id', '=', id)])
            order_line = env['sale.order.line'].sudo().search([('order_id', '=', order_id.id)])
            data = {
                'id': order_id.id,
                'name': order_id.name,
                'state': order_id.x_state,
                'address_id': {
                    'id': order_id.address_id.id,
                    'address': order_id.address_id.address,
                    'address_detail': order_id.address_id.address_detail,
                },
                'delivery_emp_id': {
                    'id': order_id.delivery_emp_id.id,
                    'name': order_id.delivery_emp_id.name,
                    'phone': order_id.delivery_emp_id.mobile,
                },
                'amount_total': order_id.x_amount_total,
                'product_ids': [
                    {
                        'id': item.id,
                        'product_name': item.x_product_id.name,
                        'product_uom_qty': item.product_uom_qty,
                        'price_subtotal': item.x_price_subtotal,
                        'sugar': item.sugar,
                        'ice': item.ice,
                        'size_id': {
                            'id': item.size_id.id,
                            'name': item.size_id.name,
                        },
                        'topping_ids': [
                            {
                                'id': i.id,
                                'name': i.name,
                            } for i in item.topping_ids
                        ],
                    } for item in order_line
                ],
                'rating_emp': float(order_id.rating_emp),
                'rating_product': float(order_id.rating_product),
                'rating_detail': order_id.rating_detail,
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def create_sale_order(self, cr, env, params):
        try:
            product_ids = params.get('product_ids')
            address_id = params.get('address_id')
            payment_method = params.get('payment_method')
            note = params.get('note')
            vals_order = {
                'partner_id': env.user.partner_id.id,
                'user_id': env.user.id,
                'x_state': 'pending',
                'address_id': address_id,
                'payment_method': payment_method,
                'note': note,
                'x_amount_total': sum(i.get('price_unit', 0) * i.get('quantity', 1) for i in product_ids),
            }
            order_id = env['sale.order'].sudo().create(vals_order)

            for product in product_ids:
                line_vals = {
                    'order_id': order_id.id,
                    'x_product_id': product.get('id'),
                    'product_uom_qty': product.get('quantity'),
                    'x_price_subtotal': product.get('price_unit') * product.get('quantity'),
                    'sugar': product.get('sugar'),
                    'ice': product.get('ice'),
                    'size_id': product.get('size_id'),
                    'topping_ids': [(6, 0, [item.get('id') for item in product.get('topping_ids')])],
                }
                env['sale.order.line'].sudo().create(line_vals)

            data = {
                'id': order_id.id,
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def cancel_sale_order(self, cr, env, params):
        id = params.get('id')
        order_id = env['sale.order'].sudo().search([('id', '=', id)])

        if not order_id:
            raise ApiException('Không có đơn hàng trên hệ thống', ApiException.UNKNOWN_ERROR)
        if order_id.x_state != 'pending':
            raise ApiException('Bạn không thể hủy đơn hàng', ApiException.UNKNOWN_ERROR)

        try:
            order_id.write({'x_state': 'cancel'})
            return {'id': order_id.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_orders_employee(self, cr, env, params):
        try:
            data = {
                'new': [],
                'history': [],
            }
            domain = [('delivery_emp_id', '=', env.user.partner_id.id)]
            order_ids = env['sale.order'].sudo().search(domain, order='id desc')

            for order in order_ids:
                date_order = order.date_order.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
                vals = {
                    'id': order.id,
                    'name': order.name,
                    'state': order.x_state,
                    'date_order': date_order,
                    'amount_total': order.x_amount_total,
                }
                if order.x_state in ['waiting', 'delivering']:
                    data['new'].append(vals)
                elif order.x_state in ['delivered', 'done']:
                    data['history'].append(vals)
            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def get_order_detail_employee(self, cr, env, params):
        try:
            id = params.get('id')
            order_id = env['sale.order'].sudo().search([('id', '=', id)])
            order_line = env['sale.order.line'].sudo().search([('order_id', '=', order_id.id)])
            data = {
                'id': order_id.id,
                'name': order_id.name,
                'state': order_id.x_state,
                'partner_id': {
                    'id': order_id.partner_id.id,
                    'name': order_id.partner_id.name,
                    'phone': order_id.partner_id.phone,
                },
                'address_id': {
                    'id': order_id.address_id.id,
                    'address': order_id.address_id.address,
                    'address_detail': order_id.address_id.address_detail,
                    'lat': order_id.address_id.lat,
                    'long': order_id.address_id.long,
                },
                'amount_total': order_id.x_amount_total,
                'product_ids': [
                    {
                        'id': item.id,
                        'product_name': item.x_product_id.name,
                        'product_uom_qty': item.product_uom_qty,
                        'price_subtotal': item.x_price_subtotal,
                        'sugar': item.sugar,
                        'ice': item.ice,
                        'size_id': {
                            'id': item.size_id.id,
                            'name': item.size_id.name,
                        },
                        'topping_ids': [
                            {
                                'id': i.id,
                                'name': i.name,
                            } for i in item.topping_ids
                        ],
                    } for item in order_line
                ]
            }

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def update_sale_order(self, cr, env, params):
        id = params.get('id')
        action = params.get('action')
        order_id = env['sale.order'].sudo().search([('id', '=', id)])
        user_devices = env['res.users.device'].search(
            [('user_id.partner_id', '=', order_id.partner_id.id)])

        if not order_id:
            raise ApiException('Không có đơn hàng trên hệ thống', ApiException.UNKNOWN_ERROR)

        if action == 'finish':
            domain_update = {'x_state': 'delivered'}
            for item in user_devices:
                env['kct.res.notification'].sudo().create({
                    'user_device_id': item.id,
                    'model': 'sale.order',
                    'res_id': order_id.id,
                    'message': f"Đơn hàng đã giao đến bạn thành công.",
                })
        elif action == 'receive':
            domain_update = {'x_state': 'delivering'}
            for item in user_devices:
                env['kct.res.notification'].sudo().create({
                    'user_device_id': item.id,
                    'model': 'sale.order',
                    'res_id': order_id.id,
                    'message': f"Đơn hàng đang được giao đến bạn.",
                })
        elif action == 'reject':
            domain_update = {'x_state': 'received', 'delivery_emp_id': None}
        else:
            raise ApiException('Hành động không hợp lệ', ApiException.UNKNOWN_ERROR)

        try:
            order_id.write(domain_update)
            return {'id': order_id.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def rating_sale_order(self, cr, env, params):
        id = params.get('id')
        rating_emp = params.get('rating_emp')
        rating_product = params.get('rating_product')
        rating_detail = params.get('rating_detail')
        order_id = env['sale.order'].sudo().search([('id', '=', id)])

        if not order_id:
            raise ApiException('Không có đơn hàng trên hệ thống', ApiException.UNKNOWN_ERROR)

        try:
            order_id.write({
                'x_state': 'done',
                'rating_emp': rating_emp,
                'rating_product': rating_product,
                'rating_detail': rating_detail,
            })
            return {'id': order_id.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
