# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    fee_id = fields.Many2one('billing.fee', string='Billing Fee')
