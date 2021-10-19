from odoo import models, fields, _


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    driver_id = fields.Many2one(related=False)
    transport_id = fields.Many2one('transport.order')
