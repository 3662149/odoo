# -*- coding: utf-8 -*-
from odoo import models, fields, _


class EndCargoWizard(models.TransientModel):
    _name = 'end.cargo.wizard'
    _description = 'End cargo wizard'

    transport_id = fields.Many2one('transport.order', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', required=True)
    burned_fuel = fields.Float(required=True)
    fuel_price_unit = fields.Float(required=True)
    internal_note = fields.Char()
    add_service_log = fields.Boolean()

    def confirm(self):
        self.transport_id.write({
            'internal_note': self.transport_id.internal_note or "" + _("\n END TRIP NOTE:\n" + "" or self.internal_note),
            'state': 'delivered', 'burned_fuel': self.burned_fuel})
        last_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id)], limit=1,
                                                                  order='value desc')
        if last_odometer:
            last_odometer = last_odometer.value
        else:
            last_odometer = 0
        self.env['fleet.vehicle.odometer'].create({
            'value': last_odometer + self.transport_id.distance or 0,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.transport_id.driver_id.user_partner_id.id,
            'transport_id': self.transport_id.id
        })
        fuel_log_id = self.env['fleet.vehicle.log.fuel'].create({
            'liter': self.burned_fuel,
            'price_per_liter': self.fuel_price_unit,
            'purchaser_id': self.transport_id.driver_id.user_partner_id.id,
            'transport_id': self.transport_id.id
        })
        fuel_log_id._onchange_liter_price_amount()
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
