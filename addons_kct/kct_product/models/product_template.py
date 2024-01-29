from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = 'kct.product'

    name = fields.Char(string='Tên sản phẩm', required=True)
    description = fields.Char(string='Mô tả')
    price = fields.Float(string='Giá', default=0, required=True)
    image = fields.Image(string="Ảnh")
    all_size = fields.Boolean(string="Tất cả kích thước", default=False)
    all_topping = fields.Boolean(string="Tất cả topping", default=False)
    has_sugar = fields.Boolean(string="Có đường", default=True)
    has_ice = fields.Boolean(string="Có đá", default=True)
    category_id = fields.Many2one('product.category', string="Danh mục sản phẩm", required=True)
    size_ids = fields.Many2many('kct.product.size', string="Danh mục kích thước")
    topping_ids = fields.Many2many('kct.product.topping', string="Danh mục topping")

    @api.onchange('all_size')
    def onchange_all_size(self):
        if self.all_size:
            sizes = self.env['kct.product.size'].search([])
            self.size_ids = [(6, 0, [item.id for item in sizes])]
        else:
            self.size_ids = [(5, 0, 0)]

    @api.onchange('all_topping')
    def onchange_all_topping(self):
        if self.all_topping:
            toppings = self.env['kct.product.topping'].search([])
            self.topping_ids = [(6, 0, [item.id for item in toppings])]
        else:
            self.topping_ids = [(5, 0, 0)]
