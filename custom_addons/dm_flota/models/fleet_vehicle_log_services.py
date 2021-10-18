from odoo import models, fields, _


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    transport_id = fields.Many2one('transport.order')
