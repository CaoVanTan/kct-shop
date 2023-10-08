# -*- coding: utf-8 -*-
from odoo import fields, models


class KctProductSize(models.Model):
    _name = 'kct.product.category'
    _description = 'KCT Product Category'

    name = fields.Char(string='Tên danh mục', required=True)
