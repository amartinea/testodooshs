# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BillingFee(models.Model):
    _name = "billing.fee"

    name = fields.Char('Name')
    sequence = fields.Integer(help='Used to order billing fee', default=10)
    fee_lines = fields.One2many('billing.fee.lines', 'fee_id', string='Billing Fee lines', readonly=False)
    tax_id = fields.Many2one('account.tax', string='Tax apply to fee')
    account_id = fields.Many2one('account.account', string="Account")

    def _check_condition_to_apply(self, vals):
        for line in self.fee_lines:
            if line.condition == 'big' and line._calcul_condition_bigger(vals):
                return line
            elif line.condition == 'smal' and line._calcul_condition_smaller(vals):
                return line
            elif line.condition == 'bet' and line._calcul_condition_between(vals):
                return line 
        return False


class BillingFeeLines(models.Model):
    _name = "billing.fee.lines"

    value_condition1 = fields.Float('Value 1')
    value_condition2 = fields.Float('Value 2')
    value_apply = fields.Float('Fee Value')
    value_type = fields.Selection([('perc', '%'), ('fix', 'fix')], required=True, default='fix')
    condition = fields.Selection([('big', 'Bigger or egal'), ('smal', 'Smaller or egal'), ('bet', 'Between')], required=True, default='big')
    sequence = fields.Integer(help='Used to order billing fee lines', default=10)
    fee_id = fields.Many2one('billing.fee', string='Billing Fee')


    def _calcul_condition_bigger(self, vals):
        if self.value_condition1 > vals:
            return False
        return True


    def _calcul_condition_smaller(self, vals):
        if self.value_condition1 < vals:
            return False
        return True

    def _calcul_condition_between(self, vals):
        if self.value_condition1 > vals or self.value_condition2 < vals:
            return False
        return True
