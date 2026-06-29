# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date,datetime, timedelta
import requests



class MRP(models.Model):
    _inherit = "mrp.production"

    is_child_mo = fields.Boolean(default=False)
    delivery_date = fields.Date(string='Delivery Date')


    def button_mark_done(self):
        res = super(MRP, self).button_mark_done()
        if self.origin:
            get_sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)])
            if get_sale_order_id and get_sale_order_id.analytic_account_id.id:
                rec_for_component_total = self.env['report.mrp_account_enterprise.mrp_cost_structure'].get_lines(self)
                # create line for total cost of component
                if rec_for_component_total[0]['total_cost'] != 0:
                    self.env['account.analytic.line'].create({
                        'date': self.date_planned_start,
                        'name': "Total Cost Of Component" + "-" + rec_for_component_total[0]['product'].name,
                        'account_id': get_sale_order_id.analytic_account_id.id,
                        'amount': rec_for_component_total[0]['total_cost'] * -1,
                    })
                # create line for total cost of operation
                total_cost_of_op = 0
                for op in rec_for_component_total[0]['operations']:
                    total_cost_of_op = total_cost_of_op + op[3] * op[4]
                self.env['account.analytic.line'].create({
                    'date': self.date_planned_start,
                    'name': "Total Cost Of Operations",
                    'account_id': get_sale_order_id.analytic_account_id.id,
                    'amount': total_cost_of_op * -1,
                })

            get_mo_id = self.env['mrp.production'].search([('name', '=', self.origin)])
            get_sale_order_id_for_child_mo = self.env['sale.order'].search([('name', '=', get_mo_id.origin)])
            if get_sale_order_id_for_child_mo and get_sale_order_id_for_child_mo.analytic_account_id.id:
                rec_for_component_total_for_child = self.env[
                    'report.mrp_account_enterprise.mrp_cost_structure'].get_lines(self)
                # create line for total cost of component
                if rec_for_component_total_for_child[0]['total_cost'] != 0:
                    self.env['account.analytic.line'].create({
                        'date': self.date_planned_start,
                        'name': "Total Cost Of Component" + "-" + rec_for_component_total_for_child[0]['product'].name,
                        'account_id': get_sale_order_id_for_child_mo.analytic_account_id.id,
                        'amount': rec_for_component_total_for_child[0]['total_cost'] * -1,
                    })
                # create line for total cost of operation
                total_cost_of_op_for_child = 0
                for op_1 in rec_for_component_total_for_child[0]['operations']:
                    total_cost_of_op_for_child = total_cost_of_op_for_child + op_1[3] * op_1[4]
                self.env['account.analytic.line'].create({
                    'date': self.date_planned_start,
                    'name': "Total Cost Of Operations",
                    'account_id': get_sale_order_id_for_child_mo.analytic_account_id.id,
                    'amount': total_cost_of_op_for_child * -1,
                })

        if self.reservation_state != 'assigned':
            raise UserError(_('All components must be available and reserved 100% before marking the MO as done.'))

        return res

    # def send_sms(self, sale_id, message):
    #     api_key = self.env['ir.config_parameter'].sudo().get_param('sms_textlocal.textlocal_api_key')
    #     if not api_key:
    #         raise UserError(_("Please define API key on general settings!"))
    #     numbers = sale_id.partner_id.mobile
    #     url = "https://api.textlocal.in/send/?apiKey=" + api_key + '&' + 'sender=INVBED&' + 'numbers=' + numbers + '&message=' + message + ''
    #     payload = {}
    #     headers = {}
    #     response = requests.request("GET", url, headers=headers, data=payload)
    #     data = response.json()
    #     status = data.get('status')
    #     sms_log = self.env["smstextlocal.logs"]
    #     if status == 'success':
    #         sms_log.create({'partner_id': sale_id.partner_id.id, 'mobile': numbers, 'record_id': self.id, 'reference': self.name, 'message': message, 'state': 'delivered', 'log': data})
    #     else:
    #         sms_log.create({'partner_id': sale_id.partner_id.id, 'mobile': numbers, 'record_id': self.id, 'reference': self.name, 'message': message, 'state': 'fail', 'log': data})

    def action_confirm(self):
        self._check_company()
        for production in self:
            sale_orders = production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
            if any(not sale.auto_confirm_mrp for sale in sale_orders):
                return True
            if production.mrp_production_source_count > 0 and not production.is_child_mo:
                production.is_child_mo = True
                return True
            sale_id = self.env['sale.order'].sudo().search([('name', '=', production.origin)], limit=1)
            if sale_id and sale_id.team_id.id in [1, 3, 25, 26] and sale_id.partner_id:
                customer = sale_id.partner_id.name[0:20]
                email_to = sale_id.partner_id.email
                order_raw_material_procured = self.env.ref('mrp_extended.mail_template_mo_confirm')
                order_raw_material_procured.with_context(email_to=email_to, customer=customer).send_mail(production.id)
                message = "Dear " + (customer) + "\nWe are glad to inform you that your order is in production and we will update you soon with the next progress.\n-Team Invisible bed"
                if sale_id.partner_id.mobile:
                    self.send_sms(sale_id, message)
        return super(MRP, self).action_confirm()

    def _mo_reminder_cron(self):
        email = self.env.user.email
        is_check_mail = self.env['ir.config_parameter'].sudo().get_param('mrp.mail_before_scheduled_day')
        days_before_mail = self.env['ir.config_parameter'].sudo().get_param('mrp.mail_mo_days')
        if is_check_mail:
            template = self.env.ref('mrp_extended.mrp_mo_reminder_mail_template')
            mo_ids = self.search([]).filtered(lambda x: x.state == 'confirmed' and (x.date_planned_start.date() - fields.Date.today()).days == int(days_before_mail))
            for user in mo_ids.mapped('user_id'):
                mo_name = mo_ids.filtered(lambda x: x.user_id == user).mapped('name')
                email_to = user.partner_id.email
                template.with_context(mo_ids=mo_name, from_email=email, email_to=email_to).sudo().send_mail(self.id)


    # Scheduled action to send shipment status plan reminder emails.
    # def _shipment_status_plan_cron(self):
    #     is_check_shipment_mail = self.env['ir.config_parameter'].sudo().get_param('stock.shipment_status_plan_reminder_mail')
    #     is_check_daily_shipment_mail = self.env['ir.config_parameter'].sudo().get_param('stock.daily_shipment_status_plan_reminder_mail')
    #
    #     if is_check_shipment_mail and int(date.today().weekday()) == int(self.env.company.week_day_shipment_mail):
    #         self._call_email_template_shipment_status()
    #     if is_check_daily_shipment_mail:
    #         self._call_email_template_shipment_status()

        # Send shipment status plan email to configured users.

    def _call_email_template_shipment_status(self):
        email = self.env.user.email
        template = self.env.ref('mrp_extended.shipment_status_plan_reminder_mail_template')
        shipment_ids = self.search([]).filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.scheduled_date.year == date.today().year and x.scheduled_date.strftime("%V") == date.today().strftime("%V"))
        data = []
        for picking in shipment_ids:
            data.append({
                'dispatch': picking.name,
                'sales_no': picking.origin,
                'scheduled_date': picking.scheduled_date.date(),
                'status': picking.states,
            })
        for user in self.env.company.user_ids_shipment:
            email_to = user.partner_id.email
            template.with_context(shipment_ids=data, from_email=email, email_to=email_to).sudo().send_mail(self.id)






