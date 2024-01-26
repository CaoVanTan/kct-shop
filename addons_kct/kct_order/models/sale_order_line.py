from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    _sql_constraints = [
        ('accountable_required_fields',
         "CHECK(1=1)",
         "Missing required fields on accountable sale order line."),
        ('non_accountable_null_fields',
         "CHECK(1=1)",
         "Forbidden values on non-accountable sale order line"),
    ]

    price_unit = fields.Float(required=False)
    name = fields.Text(required=False)
    customer_lead = fields.Float(required=False)
    product_uom_qty = fields.Float(required=False)

    x_product_id = fields.Many2one('kct.product')
    x_price_subtotal = fields.Float(string="Tổng giá")
    size_id = fields.Many2one('kct.product.size', string="Kích thước")
    topping_ids = fields.Many2many('kct.product.topping', string="Topping")
    sugar = fields.Char(string="Mức đường")
    ice = fields.Char(string="Mức đá")
    x_price_unit = fields.Float(related='x_product_id.price', readonly=True)
    topping_compute = fields.Char(string='Topping', compute='_topping_computed_field', readonly=True)

    @api.depends('topping_ids')
    def _topping_computed_field(self):
        for record in self:
            formatted_toppings = "<br/>".join(item.name for item in record.topping_ids)
            record.topping_compute = f"<p>{formatted_toppings}</p>"
