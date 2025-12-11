# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    def _email_sfg_product_qty_cron(self):
        """
        Scheduled action to send SFG/FG product on-hand quantity email.
        Sends weekly email with product quantities to configured users.
        """
        email = self.env.user.email

        is_check_product_qty = self.env['ir.config_parameter'].sudo().get_param('product.on_hand_qty_send_mail')

        if int(date.today().weekday()) == int(self.env.company.week_day_product_qty):
            if is_check_product_qty:
                template = self.env.ref('custom_sale_mrp.sfg_product_on_hand_qty_mail_template')

                product_ids = self.search([]).filtered(lambda x: x.bom_count > 0 and x.qty_available > 0)
                data = []
                for product in product_ids:
                    data.append({
                        'name': product.name,
                        'on_hand_qty': product.qty_available,
                    })
                for user in self.env.company.user_ids_product_qty:
                    email_to = user.partner_id.email
                    template.with_context(product_ids=data, from_email=email, email_to=email_to).sudo().send_mail(self.id)