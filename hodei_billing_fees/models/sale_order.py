# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fee_price = fields.Float('Billing Fee', store=True, default="0")
    apply_fee = fields.Boolean(string='Apply Fee', default=True)

    @api.model
    def create(self, vals):
        _logger.warning(self)
        _logger.warning(vals)
        amount_change = 0
        if vals.get('order_line'):
            for line in vals['order_line']:
                _logger.warning(line[0])
                if line[0] == 0:
                    amount_change += line[2]['product_uom_qty'] * line[2]['price_unit']
                    _logger.warning(amount_change)
                elif line[0] == 2:
                    amount_change -= self.env['sale.order.line'].search([('id', '=', line[1])])['price_subtotal']
        _logger.warning(vals['partner_id'])
        if vals['apply_fee']:
            partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            fee_line = partner.fee_id._check_condition_to_apply(amount_change)
            if fee_line:
                if fee_line.value_type == 'perc':
                    fee_price = vals['amount_untaxed'] * fee_line.value_apply / 100
                elif fee_line.value_type == 'fix':
                    fee_price = fee_line.value_apply
            else:
                fee_price = 0
        else:
            fee_price = 0
        if fee_price != 0:
            sale_line_data = {
                'name': 'Billing Fee',
                'product_id': self.env.ref('hodei_billing_fees.product_fees').id,
                'tax_id': [(6, 0, [partner.fee_id.tax_id.id])],
                'price_unit': fee_price,
                'price_subtotal': fee_price,
                'price_total': fee_price,
                'product_uom_qty': 1,
                'qty_delivered': 1,
                'discount': 0,
                'company_id': 1,
                'currency_id': 1
            }
            if vals.get('order_line'):
                vals['order_line'] += [(0, 0, sale_line_data)]
            else:
                vals['order_line'] = [(0, 0, sale_line_data)]
        vals['fee_price'] = fee_price
        return super(SaleOrder, self).create(vals)

    @api.model
    def write(self, values):
        _logger.warning(self)
        _logger.warning(values)
        amount_change = 0
        if values.get('order_line'):
            for line in values['order_line']:
                _logger.warning(line[0])
                if line[0] == 0:
                    amount_change += line[2]['product_uom_qty'] * line[2]['price_unit']
                    _logger.warning(amount_change)
                elif line[0] == 2:
                    amount_change -= self.env['sale.order.line'].search([('id', '=', line[1])])['price_subtotal']
                    _logger.warning(amount_change)
            _logger.warning('_________________amount_change')
            _logger.warning(amount_change)
        if self.apply_fee:
            fee_line = self.partner_id.fee_id._check_condition_to_apply(self.amount_untaxed + amount_change)
            if fee_line:
                if fee_line.value_type == 'perc':
                    fee_price = self.amount_untaxed * fee_line.value_apply / 100
                elif fee_line.value_type == 'fix':
                    fee_price = fee_line.value_apply
            else:
                fee_price = 0
        else:
            fee_price = 0
        _logger.warning(self.fee_price)
        _logger.warning('_________________fee_price')
        _logger.warning(fee_price)
        if self.fee_price != fee_price:
            product_fee = self.env['product.product'].search([('fee_product', '=', True)])
            billing_line = self.env['sale.order.line'].search(
                [('order_id', '=', self.id), ('product_id', '=', product_fee.id)])
            _logger.warning('_________________billing_line')
            _logger.warning(billing_line)
            if billing_line:
                sale_line_data = {
                    'price_unit': fee_price
                }
                if values.get('order_line'):
                    values['order_line'] += [(1, billing_line.id, sale_line_data)]
                else:
                    values['order_line'] = [(1, billing_line.id, sale_line_data)]
                # sale_line_data = {
                #     'price_unit': fee_price,
                #     'price_subtotal': fee_price,
                #     'price_total': fee_price,
                #     'price_subtotal_signed': fee_price,
                # }
                _logger.warning('_________________sale_line_data')
                _logger.warning(sale_line_data)
            else:
                sale_line_data = {
                    'name': 'Billing Fee',
                    'product_id': self.env.ref('hodei_billing_fees.product_fees').id,
                    'tax_id': [(6, 0, [self.partner_id.fee_id.tax_id.id])],
                    'price_unit': fee_price,
                    'price_subtotal': fee_price,
                    'price_total': fee_price,
                    'product_uom_qty': 1,
                    'qty_delivered': 1,
                    'discount': 0,
                    'company_id': 1,
                    'currency_id': 1
                }
                _logger.warning('_________________sale_line_data2')
                _logger.warning(sale_line_data)
                if sale_line_data:
                    if values.get('order_line'):
                        values['order_line'] += [(0, 0, sale_line_data)]
                    else:
                        values['order_line'] = [(0, 0, sale_line_data)]
                    _logger.warning('_________________values')
                    _logger.warning(values)
            values['fee_price'] = fee_price
        return super(SaleOrder, self).write(values)
