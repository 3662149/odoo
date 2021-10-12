# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportOrderLine(models.Model):
    _name = 'transport.order.line'
    _description = 'Transport Order Line model'

    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', required=True)
    transport_id = fields.Many2one('transport.order', required=True)
    tax_ids = fields.Many2many('account.tax', required=True)
    quantity = fields.Float(default=0)
    product_uom_id = fields.Many2one(related='product_id.uom_id', readonly=True, required=True)
    price_unit = fields.Monetary(required=True, default=0)
    discount= fields.Integer(default=0)
    label = fields.Char()
    currency_id = fields.Many2one(related='transport_id.currency_id', readonly=True)
    price_net = fields.Monetary(compute='_compute_line_values', readonly=True)
    price_vat = fields.Monetary(compute='_compute_line_values', readonly=True)
    price_total = fields.Monetary(compute='_compute_line_values', readonly=True)

    @api.onchange('tax_ids', 'product_id')
    def _onchange_tax(self):
        if self.discount and (self.discount > 100 or self.discount < 0):
            raise ValidationError(_('Discount must be greater than 0 and less than 100'))
        if len(self.tax_ids.ids) > 1:
            raise ValidationError(_('It can be only one tax in line !'))

    @api.depends('price_unit', 'quantity', 'tax_ids', 'discount')
    def _compute_line_values(self):
        for line in self:
            line.price_net = 0
            line.price_vat = 0
            line.price_total = 0
            if line.price_unit and len(line.tax_ids):
                line.price_net = ((line.price_unit if not line.tax_ids.price_include else line.price_unit * (1 - (line.tax_ids.amount / 100))) * line.quantity) * (1 - line.discount / 100)
                line.price_total = ((line.price_unit if line.tax_ids.price_include else line.price_unit * (1 + (line.tax_ids.amount / 100))) * line.quantity) * (1 - line.discount / 100)
                line.price_vat = line.price_total - line.price_net

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.label = self.product_id.name
            # self.product_uom_id = self.product_id.product_tmpl_id.uom_id
            self.price_unit = self.product_id.lst_price
            self.tax_ids = self.product_id.taxes_id[0] if self.product_id.taxes_id else False
            self._compute_line_values()
