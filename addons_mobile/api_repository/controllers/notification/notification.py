from odoo.http import Controller
from ..helpers import ApiException
import pytz


class Notification(Controller):

    def get_notifications(self, cr, env, params):
        try:
            data = []
            base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value + '/api'

            for device in env.user.device_ids:
                if device.device_id == params.get('device_id'):
                    notifications = env['kct.res.notification'].sudo().search([('user_device_id', '=', device.id)],
                                                                              order='id desc')
                    for item in notifications:
                        if item.model == 'sale.order':
                            order_line = env['sale.order.line'].sudo().search([('order_id', '=', item.res_id)],
                                                                              limit=1)
                            create_date = item.create_date.replace(tzinfo=pytz.UTC).astimezone(
                                pytz.timezone('Asia/Ho_Chi_Minh'))

                            image_url = f'{base_url}/web/image2/kct.product/{order_line.x_product_id.id}/image'
                            data.append({
                                'id': item.id,
                                'model': item.model,
                                'res_id': item.res_id,
                                'state': item.state,
                                'title': item.title,
                                'message': item.message,
                                'create_date': create_date,
                                'image': image_url,
                            })

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
