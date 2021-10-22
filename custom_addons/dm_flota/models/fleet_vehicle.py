from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    average_fuel_consumption = fields.Float(readonly=True, help='Compute based on finished transport once per day')
    lifting_capacity = fields.Float(required=True)
    curb_weight = fields.Float(required=True)
    free_capacity = fields.Float(readonly=True, compute='_compute_free_capacity')

    def _compute_average_fuel_consumption(self):
        for vehicle in self.env['fleet.vehicle'].search([]):
            average_list = []
            fuel_logs = vehicle.env['fleet.vehicle.log.fuel'].search(
                [('transport_id', '!=', False), ('vehicle_id', '=', vehicle.id)])
            for fuel_log in fuel_logs:
                if fuel_log.transport_id.distance:
                    average_list.append(round((fuel_log.liter / fuel_log.transport_id.distance) * 100, 2))
            if average_list:
                vehicle.average_fuel_consumption = round(sum(average_list) / len(average_list), 2)

    def _compute_free_capacity(self):
        for vehicle in self:
            vehicle.write({'free_capacity': 0}) #TODO jak pofixuje dane to wywalic ta linie
            if vehicle.lifting_capacity and vehicle.curb_weight: #TODO jak pofixuje dane to wywalic ta linie
                vehicle.write({'free_capacity': vehicle.lifting_capacity - vehicle.curb_weight})
4