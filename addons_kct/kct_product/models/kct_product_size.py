# -*- coding: utf-8 -*-
from odoo import fields, models


class KctProductSize(models.Model):
    _name = 'kct.product.size'
    _description = 'KCT Product Size Category'

    name = fields.Char(string='Tên danh mục', required=True)
    price = fields.Float(string='Giá', default=0, require=True)
