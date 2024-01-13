from odoo import api, fields, models


class ResAddress(models.Model):
    _name = 'kct.res.address'

    address = fields.Char(required=True)
    address_detail = fields.Char()
    label = fields.Char(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    selected = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner', required=True)

    @api.model
    def create(self, values):
        existing_record = self.search([('partner_id', '=', values.get('partner_id')), ('selected', '=', True)])
        if not existing_record:
            values['selected'] = True

        return super(ResAddress, self).create(values)

    @api.model
    def write(self, values):
        if values.get('selected'):
            other_records = self.search([('partner_id', '=', self.partner_id.id), ('id', '!=', self.id)])
            other_records.write({'selected': False})

        return super(ResAddress, self).write(values)

    @api.model
    def unlink(self):
        other_record = self.search([('partner_id', '=', self.partner_id.id), ('id', '!=', self.id)], limit=1)
        if other_record:
            other_record.write({'selected': True})

        return super(ResAddress, self).unlink()
