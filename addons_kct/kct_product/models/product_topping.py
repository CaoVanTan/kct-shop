from odoo import fields, models


class ProductTopping(models.Model):
    _name = 'kct.product.topping'
    _description = 'KCT Product Topping Category'

    name = fields.Char(string='Danh mục', required=True)
    price = fields.Float(string='Giá', default=0, require=True)
