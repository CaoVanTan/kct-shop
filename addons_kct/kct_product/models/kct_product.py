# -*- coding: utf-8 -*-
from odoo import fields, models


class KctProduct(models.Model):
    _name = 'kct.product'
    _description = 'KCT Product'

    name = fields.Char(string='Tên sản phẩm', required=True)
    description = fields.Char(string='Mô tả')
    price = fields.Float(string='Giá', default=0, require=True)
    rating = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Đánh giá")
    image = fields.Image(string="Ảnh")
    all_size = fields.Boolean(string="Tất cả kích thước", default=False)
    all_topping = fields.Boolean(string="Tất cả topping", default=False)
    has_sugar = fields.Boolean(string="Có đường", default=True)
    has_ice = fields.Boolean(string="Có đá", default=True)

    category_id = fields.Many2one('kct.product.category', string="Loại sản phẩm", required=True)
    size_id = fields.Many2many('kct.product.size', string="Loại kích thước" , required=True)
    topping_id = fields.Many2many('kct.product.topping', string="Loại topping" , required=True)
