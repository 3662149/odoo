# -*- coding: utf-8 -*-
from odoo import models, fields, _


class EndCargoWizard(models.TransientModel):
    _name = 'end.cargo.wizard'
    _description = 'End cargo wizard'

    transport_id = fields.Many2one('transport.order', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', required=True)
    internal_note = fields.Char()
    add_service_log = fields.Boolean()

    def confirm(self):
        self.transport_id.internal_note += _("\n END TRIP NOTE:\n")
        if self.add_service_log:
            pass
        return True