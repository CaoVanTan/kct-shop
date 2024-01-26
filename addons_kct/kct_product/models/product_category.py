from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    image = fields.Image(string='Ảnh')
    description = fields.Char(string='Mô tả danh mục')
