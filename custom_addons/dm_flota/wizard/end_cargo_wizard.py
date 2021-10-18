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
        self.transport_id.write({
            'internal_note': self.transport_id.internal_note or "" + _("\n END TRIP NOTE:\n" + self.internal_note),
            'state': 'delivered'})
        if self.add_service_log:
            return {
                'name': _('Add car service'),
                'view_type': 'form',
                'res_model': 'fleet.vehicle.log.services',
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'context': {'default_transport_id': self.transport_id.id, 'default_vehicle_id': self.vehicle_id.id},
                'target': 'current'
            }
        return True
