from odoo import models, fields, _


class FleetVehicleLogFuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    transport_id = fields.Many2one('transport.order')
