# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    operator_ids = fields.Many2many('mrp.operator', string='Operators')

    @api.onchange('workcenter_id')
    def onchange_workcenter_id(self):
        for record in self:
            record.operator_ids = False
            record.operator_ids = [(6, 0, record.mapped('workcenter_id.operator_ids.id'))]


class MrpOperator(models.Model):
    _name = 'mrp.operator'
    _description = 'MRP Operator'

    name = fields.Char('Name')


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    operator_ids = fields.Many2many('mrp.operator', string='Operators')
