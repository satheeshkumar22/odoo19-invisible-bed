from odoo import _, fields, models,api

class AccountMove(models.Model):
    _inherit = "account.move"

    send_payment_reminder = fields.Boolean(compute='_compute_payment_reminder',store=True)
    split_btn_visibility = fields.Boolean(compute="_compute_button")
    custom_name = fields.Char(
        string="Custom Invoice",
        readonly=False,
        default=False,
        copy=False,
        help="""Custom invoice number. Use this field to set custom name of invoice""",
    )
    vehicle_no = fields.Char(string="Vehicle NO.")
    transporter_id = fields.Char(string="Transporter")
    e_way_bill = fields.Char(string="E Way Bill")


    # Email Notification According to the Payment State
    @api.depends('payment_state')
    def _compute_payment_reminder(self):
        print("_compute_payment_reminder =============")
        for res in self:
            print("res.move_type == ", res.move_type)
            print("res.payment_state == ", res.payment_state)
            if res.move_type == 'out_invoice':
                if res.payment_state == 'partial':
                    print("Partial == ")
                    reminder_template_id = self.env.ref('account_extended.mail_template_data_payment_reminder')
                    reminder_template_id.send_mail(res.id, force_send=True)
                if res.payment_state in ('in_payment','paid'):
                    print("in payment or paid == ")
                    payment_template_id = self.env.ref('account_extended.mail_template_data_payment_complete')
                    payment_template_id.send_mail(res.id, force_send=True)
            return True

    @api.depends()
    def _compute_button(self):
        spilt = False
        for rec in self.invoice_line_ids:
            if rec.quantity > 1:
                spilt = True
                break
        if spilt:
            self.split_btn_visibility = True
        else:
            self.split_btn_visibility = False

    def button_split_invoice(self):
        lines_lst = []
        lines_to_unlink = []
        for rec in self.invoice_line_ids:
            if rec.quantity == 1:
                pass
            else:
                line_dict = {}
                for prod_qty in range(1, round(rec.quantity + 1)):
                    line_dict['product_id'] = rec.product_id.id
                    line_dict['analytic_distribution'] = rec.analytic_distribution
                    line_dict['quantity'] = 1
                    line_dict['price_unit'] = rec.price_unit
                    if rec.discount:
                        line_dict['discount'] = rec.discount
                    line_dict['tax_ids'] = rec.tax_ids.ids
                    lines_lst.append((0, 0, line_dict))
                    line_dict = {}
                lines_to_unlink.append(rec.id)
        for delete_line in lines_to_unlink:
            for invoice_rec in self.invoice_line_ids:
                if invoice_rec.id == delete_line:
                    invoice_rec.with_context(check_move_validity=False).unlink()
        for line in self.line_ids:
            line.with_context(check_move_validity=False).unlink()
        self.write({'invoice_line_ids': lines_lst})

    def action_post(self):
        for move in self:
            if move.custom_name:
                move.write({"name": move.custom_name})
        return super(AccountMove, self).action_post()

