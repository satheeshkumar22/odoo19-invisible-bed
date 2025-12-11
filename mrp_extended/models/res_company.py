# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Shipment Configuration
    user_ids_shipment = fields.Many2many('res.users', 'res_user_stock_dilevery_rel')
    week_day_shipment_mail = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], default='0')

    # Product Quantity Configuration
    user_ids_product_qty = fields.Many2many('res.users', 'res_user_product_template_rel')
    week_day_product_qty = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], default='0')
    upi_code_image = fields.Image("UPI Code", max_width=128, max_height=128)
