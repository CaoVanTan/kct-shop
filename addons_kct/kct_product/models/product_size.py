# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductSize(models.Model):
    _name = 'kct.product.size'
    _description = 'KCT Product Size Category'

    name = fields.Selection([('S', 'S'), ('M', 'M'), ('L', 'L')], string="Danh mục", required=True)
    price = fields.Float(string='Giá', default=0, require=True)
