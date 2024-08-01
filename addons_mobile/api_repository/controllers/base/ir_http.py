from odoo import models
from odoo.http import request
from odoo import SUPERUSER_ID


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def binary_content(cls, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='datas_fname', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None, env=None):
        whitelist = ['product.template', 'res.branch', 'res.partner', 'res.users', 'hr.employee']
        env = env or request.env
        obj = None
        if xmlid:
            obj = env.ref(xmlid, False)
        elif id and model in env:
            obj = env[model].browse(int(id))
        if obj._name in whitelist:
            env = env(user=SUPERUSER_ID)
        if obj and 'website_published' in obj._fields:
            if env[obj._name].sudo().search([('id', '=', obj.id), ('website_published', '=', True)]):
                env = env(user=SUPERUSER_ID)
        return super(IrHttp, cls).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token, env=env)

    def get_image(self, env, model=None, model_id=None, field='image', default=False):
        base_url = env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value
        if default:
            return f'{base_url}/web/static/src/img/placeholder.png'
        else:
            return f'{base_url}/web/image?model={model}&id={model_id}&field={field}'
