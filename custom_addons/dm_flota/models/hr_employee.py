from odoo import models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    transport_count = fields.Integer(compute='_get_transport_count')

    def _get_transport_count(self):
        for employee in self:
            employee.transport_count = employee.env['transport.order'].search_count([('driver_id', '=', employee.id)])

    def open_transports(self):
        return {
            'name': _('Transports'),
            'domain': [('driver_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'transport.order',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
