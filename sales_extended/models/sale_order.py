# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    auto_confirm_mrp = fields.Boolean()
    payment_count = fields.Integer(
        string='Payment Count', compute='_get_advance_payment', readonly=True
    )
    payment_ids = fields.One2many(
        'account.payment', 'sale_order_id', string="Payments", readonly=True
    )
    is_paid = fields.Boolean(string="Is Paid")
    advance_payment = fields.Float("Advance Payment")
    remaining_payment = fields.Float("Remaining Payment")

    # def send_sms(self, numbers, message):
    #     pdb.set_trace()
    #     api_key = self.env['ir.config_parameter'].sudo().get_param('sms_textlocal.textlocal_api_key')
    #     if not api_key:
    #         raise UserError(_("Please define API key on general settings!"))
    #     _logger.info('SMS-----%s-------%s-----------------%s', api_key, numbers, message)
    #     url = "https://api.textlocal.in/send/?apiKey=" + api_key + '&' + 'sender=INVBED&' + 'numbers=' + numbers + '&message=' + message + ''
    #     payload = {}
    #     headers = {}
    #     response = requests.request("GET", url, headers=headers, data=payload)
    #     data = response.json()
    #     status = data.get('status')
    #     sms_log = self.env["smstextlocal.logs"]
    #     if status == 'success':
    #         sms_log.create(
    #             {'partner_id': self.partner_id.id, 'mobile': numbers, 'record_id': self.id, 'reference': self.name,
    #              'message': message, 'state': 'delivered', 'log': data})
    #     else:
    #         sms_log.create(
    #             {'partner_id': self.partner_id.id, 'mobile': numbers, 'record_id': self.id, 'reference': self.name,
    #              'message': message, 'state': 'fail', 'log': data})

    def action_confirm(self):
        self.auto_confirm_mrp = False
        res = super(SaleOrder, self).action_confirm()
        self.auto_confirm_mrp = True
        for rec in self:
            if rec.mrp_production_count:
                data = self.env['procurement.group'].read_group([('sale_id', 'in', rec.ids)], ['ids:array_agg(id)'],
                                                                ['sale_id'])
                print('data == ',data)
                mrp_product_name = ''
                for item in data:
                    procurement_groups = self.env['procurement.group'].browse(item['ids'])
                    mrp_ids = list(set(procurement_groups.stock_move_ids.created_production_id.ids) | set(
                        procurement_groups.mrp_production_ids.ids))
                    mrp_objs = self.env['mrp.production'].sudo().browse(mrp_ids)
                    mrp_product_name = ', '.join(mrp_objs.mapped('product_id.name'))
                    for mrp in mrp_objs:
                        mrp.delivery_date = rec.commitment_date
            email = self.env.user.email
            if not email:
                raise UserError(_('Unable to send menufacturing order email. Please configure current user email.'))
            # Template = self.env.ref('custom_sale_mrp.mfg_order_mail_template')
            # Template.with_context(mrp_product_name=mrp_product_name, from_email=email).send_mail(rec.id)
            if rec.team_id and rec.team_id.id in [1, 3, 25, 26] and rec.partner_id:
                email_to = rec.partner_id.email
                customer = rec.partner_id.name[0:20]
                order_received_template_id = self.env.ref('custom_sale_mrp.mail_template_order_received_new')
                order_received_template_id.with_context(email_to=email_to, customer=customer).send_mail(rec._origin.id)
                message = "Dear " + (
                    customer) + " \nThanks for your Valuable order !!\nWe have received your order and forwarding the details to the production team. We will keep you updated on the next progress. \nThanks %26 Regards,\nTeam Invisible bed"
                if rec.partner_id.mobile:
                    self.send_sms(rec.partner_id.mobile, message)
        return res

    @api.onchange('commitment_date')
    def _onchange_delivery_date(self):
        print("_onchange_delivery_date  === ")
        for rec in self:
            print("commitment date == =", rec.commitment_date)
            print("mrp_production_count date == =", rec.mrp_production_count)
            if rec.commitment_date:
                if rec.mrp_production_count:
                    data = self.env['procurement.group'].read_group([('sale_id', 'in', rec.ids)], ['ids:array_agg(id)'],
                                                                    ['sale_id'])
                    print("data  === ", data)
                    mrp_product_name = ''
                    mrp_orders = ""
                    for item in data:
                        procurement_groups = self.env['procurement.group'].browse(item['ids'])
                        print("procurement_groups  == ", procurement_groups)
                        mrp_ids = list(set(procurement_groups.stock_move_ids.created_production_id.ids) | set(
                            procurement_groups.mrp_production_ids.ids))
                        print("mrp_ids  == ", mrp_ids)
                        mrp_objs = self.env['mrp.production'].sudo().browse(mrp_ids)
                        print("mrp_objs  === ", mrp_objs)
                        for mrp in mrp_objs:
                            mrp_orders += mrp.name + ','
                            mrp.delivery_date = rec.commitment_date
                    delivery_template_id = self.env.ref('sales_extended.mail_template_delivery_date')
                    print("delivery_template_id == ", delivery_template_id)
                    delivery_template_id.with_context(mrp_orders=mrp_orders,
                                                      devliery_date=rec.commitment_date).send_mail(rec._origin.id)
    def action_register_sale_advance_payment(self):
        return {
            'name': _('Register Advance Payment'),
            'res_model': 'account.sale.advance.payment.register',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _get_advance_payment(self):
        for order in self:
            payment_ids = self.env['account.payment'].search(
                [('sale_order_id', '=', order.id)]
            )
            order.payment_count = len(payment_ids)

    def action_view_payment(self):
        payments = self.env['account.payment'].search([('sale_order_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments"
        )
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for state, view in action['views'] if view != 'form'
                ]
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
