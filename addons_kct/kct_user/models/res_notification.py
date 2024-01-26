from odoo import api, fields, models
import requests


class ResNotification(models.Model):
    _name = 'kct.res.notification'

    model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    state = fields.Char(default='unseen')
    title = fields.Char(default='Thông báo')
    message = fields.Char()
    user_device_id = fields.Many2one('res.users.device', required=True)

    @api.model
    def create(self, values):
        __SERVER_KEY = 'key=AAAAOtmPcH8:APA91bHkwy0Pbip38ZkMkhGAvWGWPORjrXhpYLsXcfCE_snpfPrGZZ36CD_VmC7qdtd2588Nz68bq-h_xWcFnuM7yByyAFn_cYyU3RpRVKXNpdBcmc0PuDekd5lXMT1B9twzCHO4asTZ'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': __SERVER_KEY,
        }
        user_device = self.env['res.users.device'].browse(values['user_device_id'])
        data = {
            'to': user_device.firebase_token,
            "notification": {
                "title": values.get('title', 'Thông báo'),
                "body": values['message'],
            },
            "data": {
                "res_id": values['res_id'],
                "model": values['model'],
                "state": values.get('state', 'unseen'),
            }
        }
        if data['to']:
            requests.post('https://fcm.googleapis.com/fcm/send', json=data, headers=headers)
            return super(ResNotification, self).create(values)
        return
