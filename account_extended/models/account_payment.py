# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_order_id = fields.Many2one('sale.order', string="Sales Order")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
