# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import requests
import pdb

class Picking(models.Model):
    _inherit = 'stock.picking'

    states = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('row_material', 'Raw Material Procured'),
        ('process_start', 'Processing Start'),
        ('qc', 'QC'),
        ('packaging', 'Packaging'),
        ('out_for_delivery', 'Ready To Dispatch'),
        ('payement_received', 'Payment Received'),
        ('delivered', 'Delivered'),
        ('installation', 'Installation'),
        ('done', 'Done'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Shipment Status', compute='_compute_states',
        copy=False, index=True, readonly=True, store=True, tracking=True)
    state = fields.Selection(tracking=False)
    invoice_last_payment = fields.Float(string='Balance Amount', compute='_get_invoiced_payment')
    team_id = fields.Many2one('crm.team',string='Platform',related="sale_id.team_id",store=True)
    installation_from = fields.Datetime(string='Installation From')
    installation_to = fields.Datetime(string='Installation To')


    @api.depends('sale_id', 'origin')
    def _get_invoiced_payment(self):
        for picking in self:
            picking.invoice_last_payment = 0
            if picking.sale_id and picking.sale_id.invoice_ids:
                invoice = self.env['account.move'].sudo().search(
                    [('id', 'in', picking.sale_id.invoice_ids.ids), ('state', '=', 'posted')], limit=1)
                print("invoice == ", invoice)
                if invoice:
                    payment = self.env['account.payment'].sudo().search([('memo', '=', invoice.name)], limit=1)
                    print("payment === ", payment)
                    if payment:
                        picking.invoice_last_payment = payment.amount

    def button_row_material(self):
        self.states = 'row_material'

    def button_process_start(self):
        self.states = 'process_start'

    def button_qc(self):
        self.states = 'qc'

    def button_packaging(self):
        self.states = 'packaging'

    def button_out_for_delivery(self):
        print("button_out_for_delivery == ")
        self.states = 'out_for_delivery'
        if self.team_id.name in ['B2B', 'B2C', 'B2C-MH', 'B2B-MH']:
            print("team id name", self.team_id.name)
            print("self.partner_id.name", self.partner_id.name)
            print("partner_id email id name", self.partner_id.email)
            if self.partner_id.email and self.partner_id.name:
                print("if email and name")
                email_to = self.partner_id.email
                customer = self.partner_id.name[0:20]
                order_ready_to_dispatch = self.env.ref('stock_extended.mail_template_ready_to_dispatch')
                order_ready_to_dispatch.with_context(email_to=email_to, customer=customer).send_mail(self._origin.id)
                # if self.partner_id.mobile:
                #     message = "Dear " + (
                #         customer) + ",\nWe are very glad to inform you that your order is ready to dispatch and our dispatch team will connect with you shortly. \nTeam Invisible bed"
                #     self.send_sms(self.partner_id.mobile, message)

    def button_delivered(self):
        self.states = 'delivered'

    def button_payment_received(self):
        print("button_payment_received === ")
        self.states = 'payement_received'
        print("self.state -- ", self.states)
        print("self.team_id -- ", self.team_id.name)
        print("self.partner_id name -- ", self.partner_id.name)
        print("self.partner_id email -- ", self.partner_id.email)
        if self.team_id.name in ['B2B', 'B2C', 'B2C-MH', 'B2B-MH']:
            if self.partner_id.email and self.partner_id.name:
                email_to = self.partner_id.email
                customer = self.partner_id.name[0:20]
                amount = self.invoice_last_payment
                order_payment_received = self.env.ref('stock_extended.mail_template_payment_received')
                print("order_payment_received  == ", order_payment_received)
                order_payment_received.with_context(email_to=email_to, customer=customer, amount=amount).send_mail(
                    self._origin.id)
                # if self.partner_id.mobile:
                #     message = "Dear " + (customer) + "\nWe acknowledge the receipt of the balance payment of " + str(
                #         amount) + ". We thank you once again for the valuable order.\nTeam Invisible bed"
                    # self.send_sms(self.partner_id.mobile, message)

    def button_installation(self):
        self.states = 'installation'
        if self.team_id.name in ['B2B', 'B2C', 'B2C-MH', 'B2B-MH']:
            if self.partner_id.email and self.partner_id.name:
                email_to = self.partner_id.email
                customer = self.partner_id.name[0:20]
                date_plan = self.installation_from
                if date_plan:
                    order_installation_planned = self.env.ref(
                        'stock_extended.mail_template_installation_planned')
                    order_installation_planned.with_context(email_to=email_to, customer=customer,
                                                            date_plan=date_plan.strftime("%d-%m-%Y")).send_mail(
                        self._origin.id)
                    # if self.partner_id.mobile:
                    #     message = "Dear " + (
                    #         customer) + "\nThis is to acknowledge that your product installation is planned by " + str(
                    #         date_plan.strftime("%d-%m-%Y")) + ".\nThanks%26Regards\nTeam Invisible bed"
                        # self.send_sms(self.partner_id.mobile, message)

    def button_close(self):
        print("button_close == ")
        self.states = 'close'
        if self.team_id.name in ['B2B', 'B2C', 'B2C-MH', 'B2B-MH']:
            if self.partner_id.email and self.partner_id.name:
                email_to = self.partner_id.email
                customer = self.partner_id.name[0:20]
                date_install = self.installation_from
                if date_install:
                    order_closed_template_id = self.env.ref('stock_extended.mail_template_order_closed')
                    order_closed_template_id.with_context(email_to=email_to, customer=customer,
                                                          date_install=date_install.strftime("%d-%m-%Y")).send_mail(
                        self._origin.id)
                    # if self.partner_id.mobile:
                    #     message = "Dear " + (
                    #         customer) + "\nWe confirm that your order delivery and installation is completed on " + str(
                    #         date_install.strftime(
                    #             "%d-%m-%Y")) + "\nFor any service-related query kindly contact us at 18005470209 or mail us at support@invisiblebed com.\nWe thank you for your valuable order.\nTeam Invisible Bed"
                        # self.send_sms(self.partner_id.mobile, message)

    @api.depends('state')
    def _compute_states(self):
        for rec in self:
            rec.states = rec.state

    def button_validate(self):
        if any(picking.states != 'installation' and picking.picking_type_code == 'outgoing' and picking.team_id.id in [
            1, 3] and picking.picking_type_id.warehouse_id.id == 4 for picking in self):
            raise UserError(_('To validate, Transfer must be in installation state.'))
        return super(Picking, self).button_validate()

    # def send_sms(self, numbers, message):
    #     pdb.set_trace()
    #     api_key = self.env['ir.config_parameter'].sudo().get_param('sms_textlocal.textlocal_api_key')
    #     if not api_key:
    #         raise UserError(_("Please define API key on general settings!"))
    #     url = "https://api.textlocal.in/send/?apiKey=" + api_key + '&' + 'sender=INVBED&' + 'numbers=' + numbers + '&message=' + message + ''
    #     pdb.set_trace()
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

    def _send_pending_installation(self):
        picking_ids = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'),
                                                        ('states', '=', 'installation'),
                                                        ('installation_to', '>', fields.Date.context_today(self))])
        for picking in picking_ids:
            if picking.origin:
                sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                pending_template_id = self.env.ref(
                    'installation_sale_delivery.mail_template_install_pending_request').with_context(
                    origin=picking.origin)
                if sale_order_id:
                    pending_template_id.send_mail(2, force_send=True, raise_exception=False)
                    ticket_obj = self.env['helpdesk.ticket'].sudo()
                    title = "Pending Installation for Sales Order #" + sale_order_id.name
                    ticket_id = ticket_obj.create({'name': title,
                                                   'team_id': 3,
                                                   'partner_id': sale_order_id.partner_id.id,
                                                   'sale_order_id': sale_order_id.id})
