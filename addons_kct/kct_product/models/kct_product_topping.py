# -*- coding: utf-8 -*-
from odoo import fields, models


class KctProductTopping(models.Model):
    _name = 'kct.product.topping'
    _description = 'KCT Product Topping Category'

    name = fields.Char(string='Tên danh mục', required=True)
    price = fields.Float(string='Giá', default=0, require=True)
