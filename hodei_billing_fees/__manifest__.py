# -*- coding: utf-8 -*-

{
    'name': 'Hodei Billing Fees module',
    'version': '1.0.0',
    'category': '',
    'description': """ """,
    'depends': [
        'account',
        'sale'
    ],
    'external_dependencies': {
    },
    'data': [
        'data/hodei_billing_fees_data.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/billing_fees_views.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/product_product_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
