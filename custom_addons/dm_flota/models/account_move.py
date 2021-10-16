from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    transport_order_id = fields.Many2one('transport.order', readonly=True)
