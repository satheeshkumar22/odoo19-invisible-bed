# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # MRP Mail Configuration
    is_mo_mail = fields.Boolean(default=(lambda self: self.env['ir.config_parameter'].sudo().get_param('mrp.mail_before_scheduled_day')))
    mo_mail_days = fields.Integer(default=(lambda self: self.env['ir.config_parameter'].sudo().get_param('mrp.mail_mo_days')))

    # Shipment Configuration
    user_ids_shipment = fields.Many2many('res.users', 'res_user_stock_dilevery_rel', related="company_id.user_ids_shipment", readonly=False, domain="[('company_id', '=', company_id)]")
    is_check_shipment_mail = fields.Boolean(default=(lambda self: self.env['ir.config_parameter'].sudo().get_param('stock.shipment_status_plan_reminder_mail')))
    is_check_daily_shipment_mail = fields.Boolean(default=(lambda self: self.env['ir.config_parameter'].sudo().get_param('stock.daily_shipment_status_plan_reminder_mail')))
    week_day_shipment_mail = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], related='company_id.week_day_shipment_mail', readonly=False)

    # Product Quantity Configuration
    user_ids_product_qty = fields.Many2many('res.users', 'res_user_product_template_rel', related="company_id.user_ids_product_qty", readonly=False, domain="[('company_id', '=', company_id)]")
    is_check_product_qty = fields.Boolean(default=(lambda self: self.env['ir.config_parameter'].sudo().get_param('product.on_hand_qty_send_mail')))
    week_day_product_qty = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], related='company_id.week_day_product_qty', readonly=False)

    upi_code_image = fields.Image("UPI Code", max_width=128, max_height=128,
                                  related='company_id.upi_code_image', readonly=False)


    def set_values(self):
        """
        Save configuration settings to system parameters.
        """
        if self.is_mo_mail:
            self.env['ir.config_parameter'].sudo().set_param('mrp.mail_before_scheduled_day', True)
            self.env['ir.config_parameter'].sudo().set_param('mrp.mail_mo_days', self.mo_mail_days or 1)
        else:
            self.env['ir.config_parameter'].sudo().set_param('mrp.mail_before_scheduled_day', False)
            self.env['ir.config_parameter'].sudo().set_param('mrp.mail_mo_days', 0)

        if self.is_check_shipment_mail:
            self.env['ir.config_parameter'].sudo().set_param('stock.shipment_status_plan_reminder_mail', True)
        else:
            self.env['ir.config_parameter'].sudo().set_param('stock.shipment_status_plan_reminder_mail', False)

        if self.is_check_daily_shipment_mail:
            self.env['ir.config_parameter'].sudo().set_param('stock.daily_shipment_status_plan_reminder_mail', True)
        else:
            self.env['ir.config_parameter'].sudo().set_param('stock.daily_shipment_status_plan_reminder_mail', False)

        if self.is_check_product_qty:
            self.env['ir.config_parameter'].sudo().set_param('product.on_hand_qty_send_mail', True)
        else:
            self.env['ir.config_parameter'].sudo().set_param('product.on_hand_qty_send_mail', False)
        return super(ResConfigSettings, self).set_values()
