import base64
import io
from odoo.tools.mimetypes import guess_mimetype
from odoo.http import request
from odoo.http import route, Controller
from ..helpers import Route, ApiException


class Image(Controller):
    @route(route=Route('web/image2/<string:model>/<int:id>/<string:field>'), method=['GET'], auth='public', type='http')
    def get_image(self, model, id, field):
        try:
            model_id = request.env[model].sudo().search([('id', '=', id)])
            if model_id:
                image_data = getattr(model_id, field)
                if image_data:
                    attach_b64decode = base64.b64decode(image_data)
                    data = io.BytesIO(attach_b64decode)
                    mimetype = guess_mimetype(attach_b64decode, default='image/png')
                    return request.make_response(
                        data,
                        headers=[
                            ('Content-Type', mimetype),
                            ('Content-Disposition', f'inline; filename=image.png'),
                        ],
                    )
                else:
                    return ''
            else:
                return request.not_found()
        except Exception as e:
            return ApiException(str(e), ApiException.UNKNOWN_ERROR)
