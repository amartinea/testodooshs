# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    fee_price = fields.Float('Billing Fee', store=True, default="0")
    apply_fee = fields.Boolean(string='Apply Fee', default=True)

    @api.model
    def create(self, vals):
        amount_change = 0
        if vals.get('invoice_line_ids'):
            for line in vals['invoice_line_ids']:
                _logger.warning(line[0])
                if line[0] == 0:
                    amount_change += line[2]['quantity'] * line[2]['price_unit']
                    _logger.warning(amount_change)
                elif line[0] == 2:
                    amount_change -= self.env['account.invoice.line'].search([('id', '=', line[1])])['price_subtotal']
        _logger.warning('_________________amount_change')
        _logger.warning(amount_change)
        _logger.warning(vals['partner_id'])
        if vals.get('apply_fee'):
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
            invoice_line_data = {
                'name': 'Billing Fee',
                'product_id': self.env.ref('hodei_billing_fees.product_fees').id,
                'uom_id': 1,
                'partner_id': partner.id,
                'account_id': partner.fee_id.account_id.id,
                'invoice_line_tax_ids': [(6, False, [partner.fee_id.tax_id.id])],
                'price_unit': fee_price,
                'quantity': 1,
                'discount': 0,
                'company_id': 1,
                'currency_id': 1
            }
            if vals.get('invoice_line_ids'):
                vals['invoice_line_ids'] += [(0, 0, invoice_line_data)]
            else:
                vals['invoice_line_ids'] = [(0, 0, invoice_line_data)]
        #invoice.compute_taxes()
        vals['fee_price'] = fee_price
        _logger.warning(vals)
        invoice =super(AccountInvoice, self).create(vals)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def write(self, values):
        amount_change = 0
        if values.get('invoice_line_ids'):
            for line in values['invoice_line_ids']:
                _logger.warning(line[0])
                if line[0] == 0:
                    amount_change += line[2]['quantity'] * line[2]['price_unit']
                    _logger.warning(amount_change)
                elif line[0] == 2:
                    amount_change -= self.env['account.invoice.line'].search([('id', '=', line[1])])['price_subtotal']
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
            billing_line = self.env['account.invoice.line'].search(
                [('invoice_id', '=', self.id), ('product_id', '=', product_fee.id)])
            _logger.warning('_________________billing_line')
            _logger.warning(billing_line)
            if billing_line:
                invoice_line_data = {
                    'price_unit': fee_price
                }
                if values.get('invoice_line_ids'):
                    values['invoice_line_ids'] += [(1, billing_line.id, invoice_line_data)]
                else:
                    values['invoice_line_ids'] = [(1, billing_line.id, invoice_line_data)]
                    _logger.warning('invoice_line_data')
                    _logger.warning(invoice_line_data)
                if fee_price == 0:
                    if values.get('tax_line_ids'):
                        values['tax_line_ids'][0][2]['amount'] -= self.fee_price * 20/100
            else:
                _logger.warning('add________________________')
                invoice_line_data = {
                    'name': 'Billing Fee',
                    'product_id': self.env.ref('hodei_billing_fees.product_fees').id,
                    'uom_id': 1,
                    'origin': self.origin,
                    'invoice_id': self.id,
                    'partner_id': self.partner_id.id,
                    'account_id': self.partner_id.fee_id.account_id.id,
                    'invoice_line_tax_ids': [(6, 0, [self.partner_id.fee_id.tax_id.id])],
                    'price_unit': fee_price,
                    'price_subtotal': fee_price,
                    'price_total': fee_price,
                    'price_subtotal_signed': fee_price,
                    'quantity': 1,
                    'discount': 0,
                    'company_id': 1,
                    'currency_id': 1
                }
                if invoice_line_data:
                    if values.get('invoice_line_ids'):
                        values['invoice_line_ids'] += [(0, 0, invoice_line_data)]
                    else:
                        values['invoice_line_ids'] = [(0, 0, invoice_line_data)]
                    if values.get('tax_line_ids'):
                        values['tax_line_ids'][0][2]['amount'] += fee_price * 20/100
            values['fee_price'] = fee_price
        _logger.warning(values)
        return super(AccountInvoice, self).write(values)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('vals_list__________________')
        for vals in vals_list:
            if vals['product_id'] == self.env.ref('hodei_billing_fees.product_fees')['id']:
                invoice = self.env['account.invoice'].search([('id', '=', vals['invoice_id'])])
                for line in invoice.invoice_line_ids:
                    if line['product_id'] == self.env.ref('hodei_billing_fees.product_fees'):
                        vals_list.remove(vals)
        _logger.warning(vals_list)

        return super(AccountInvoiceLine, self).create(vals_list)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            _logger.warning('delivered__________________')
            sale_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            _logger.warning('all________________________')
            sale_orders.action_invoice_create(final=True)
        else:
            _logger.warning('else________________________')
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            _logger.warning('sale_line_obj________________________')
            _logger.warning(sale_line_obj)
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'tax_id': [(6, 0, tax_ids)],
                    'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
