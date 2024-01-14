from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_state = fields.Selection(
        [('pending', 'Chờ xác nhận'), ('received', 'Đã xác nhận'), ('waiting', 'Chờ lấy hàng'),
         ('delivering', 'Đang giao'),
         ('delivered', 'Đã giao'), ('done', 'Hoàn thành'), ('cancel', 'Hủy')], string="Trạng thái")
    x_amount_total = fields.Float(string='Tổng tiền', required=True)
    payment_method = fields.Char(string='Phương thức thanh toán', required=True)
    address_id = fields.Many2one('kct.res.address', string="Địa chỉ giao hàng", required=True, ondelete='cascade')
    delivery_emp_id = fields.Many2one('res.partner', string="Nhân viên giao hàng")
    address = fields.Char(related='address_id.address', readonly=True)
    address_detail = fields.Char(related='address_id.address_detail', readonly=True)
    address_compute = fields.Char(string='Địa chỉ giao hàng', compute='_address_computed_field', readonly=True)
    rating_emp = fields.Float(string='Đánh giá nhân viên giao hàng')
    rating_product = fields.Float(string='Đánh giá sản phẩm')
    rating_detail = fields.Char(string='Đánh giá chi tiết')

    @api.depends('address', 'address_detail')
    def _address_computed_field(self):
        for record in self:
            record.address_compute = record.address_detail + ', ' + record.address

    def action_receive(self):
        if self.x_state == 'cancel':
            raise ValidationError('Bạn không thể nhận đơn hàng, đơn hàng này đã bị hủy!')
        for record in self:
            record.write({'x_state': 'received'})
            for item in record.user_id.device_ids:
                self.env['kct.res.notification'].sudo().create({
                    'user_device_id': item.id,
                    'model': 'sale.order',
                    'res_id': record.id,
                    'message': f"Đơn hàng của bạn đã được cửa hàng xác nhận.",
                })

    def action_delivery(self):
        if not self.delivery_emp_id:
            raise ValidationError('Vui lòng chọn nhân viên giao hàng!')
        orders = self.env['sale.order'].search(
            [('delivery_emp_id.id', '=', self.delivery_emp_id.id), ('x_state', '=', 'waiting')])
        if len(orders) > 0:
            raise ValidationError('Nhân viên giao hàng không thể nhận thêm đơn hàng!')
        for record in self:
            record.write({'x_state': 'waiting'})
            user_devices = self.env['res.users.device'].search(
                [('user_id.partner_id', '=', self.delivery_emp_id.id)])
            for item in user_devices:
                self.env['kct.res.notification'].sudo().create({
                    'user_device_id': item.id,
                    'model': 'sale.order',
                    'res_id': record.id,
                    'message': f"Bạn đã nhận được đơn hàng mới.",
                })

    def action_cancel(self):
        if self.x_state == 'cancel':
            raise ValidationError('Bạn không thể hủy đơn hàng, đơn hàng này đã bị hủy trước đó!')
        view = self.env.ref('kct_order.cancel_sale_order_form')
        return {
            'name': 'Hủy đơn hàng',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def confirm_cancel_order(self):
        for record in self:
            record.write({'x_state': 'cancel', 'state': 'cancel'})
            for item in record.user_id.device_ids:
                self.env['kct.res.notification'].sudo().create({
                    'user_device_id': item.id,
                    'model': 'sale.order',
                    'res_id': record.id,
                    'message': f"Đơn hàng của bạn đã bị cửa hàng hủy bỏ.",
                })
