from odoo.http import Controller
from ..helpers import ApiException


class Address(Controller):

    def get_address(self, cr, env, params):
        try:
            data = []
            address = env['kct.res.address'].sudo().search([('partner_id', '=', env.user.partner_id.id)])
            for item in address:
                data.append({
                    'id': item.id,
                    'address': item.address,
                    'address_detail': item.address_detail,
                    'label': item.label,
                    'lat': item.lat,
                    'long': item.long,
                    'selected': item.selected,
                })

            return data
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def create_address(self, cr, env, params):
        try:
            address = params.get('address')
            address_detail = params.get('address_detail')
            label = params.get('label')
            lat = params.get('lat')
            long = params.get('long')

            vals = {
                'address': address,
                'address_detail': address_detail,
                'label': label,
                'lat': lat,
                'long': long,
                'partner_id': env.user.partner_id.id,
            }
            address_id = env['kct.res.address'].sudo().create(vals)

            return {'id': address_id.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def edit_address(self, cr, env, params):
        try:
            address_id = params.get('id')
            address = params.get('address')
            address_detail = params.get('address_detail')
            label = params.get('label')
            lat = params.get('lat')
            long = params.get('long')
            selected = params.get('selected')

            address_data = env['kct.res.address'].sudo().search([('id', '=', address_id)])
            vals = {
                'address': address,
                'address_detail': address_detail,
                'label': label,
                'lat': lat,
                'long': long,
                'selected': selected if selected else address_data.selected,
            }
            if not address_data:
                raise ApiException('Địa chỉ không tồn tại!', ApiException.UNKNOWN_ERROR)
            address_data.write(vals)

            return {'id': address_data.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)

    def delete_address(self, cr, env, params):
        try:
            address_id = params.get('id')

            address = env['kct.res.address'].sudo().search([('id', '=', address_id)])
            if not address:
                raise ApiException('Địa chỉ không tồn tại!', ApiException.UNKNOWN_ERROR)
            address.unlink()

            return {'id': address.id}
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
