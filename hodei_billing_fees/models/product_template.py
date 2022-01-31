# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fee_product = fields.Boolean('Fee product', default=False)
