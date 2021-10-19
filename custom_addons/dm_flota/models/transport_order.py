# -*- coding: utf-8 -*-
import requests
from geopy.geocoders import Nominatim
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class TransportOrder(models.Model):
    _name = 'transport.order'
    _inherit = ['mail.thread']
    _description = 'Transport Order model'

    name = fields.Char(required=True)

    partner_id = fields.Many2one('res.partner', required=True)
    place_from = fields.Many2one('transport.place', required=True, track_visibility='onchange')
    place_to = fields.Many2one('transport.place', required=True, track_visibility='onchange')
    date_of_departure = fields.Datetime(required=True, track_visibility='onchange')
    predicted_date_arrival = fields.Datetime(readonly=True, compute='_compute_date_of_departure')
    estimated_driving_time = fields.Float(readonly=True)
    distance = fields.Float(readonly=True)
    driver_id = fields.Many2one('hr.employee', required=True, track_visibility='onchange')
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, track_visibility='onchange')
    cargo_ids = fields.One2many('transport.order.line', 'transport_id', ondelete="cascade")
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.ref('base.PLN'))
    total_gross = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_net = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_vat = fields.Monetary(compute='_compute_summary_values', readonly=True)
    internal_note = fields.Char()
    state = fields.Selection([('planning', "Planning"), ('confirmed', "Confirmed"), ('on_way', "On the way"),
                              ('delivered', 'Delivered'), ('cancel', 'Cancel')], default='planning', readonly=True,
                             track_visibility='onchange')
    type = fields.Many2one('transport.type')
    invoices_count = fields.Integer(compute='_get_invoices_count')
    services_count = fields.Integer(compute='_get_services_count')
    burned_fuel = fields.Float(readonly=True)

    @api.onchange('cargo_ids')
    def _onchange_cargo_ids(self):
        cargo_weight = 0
        for line in self.cargo_ids:
            cargo_weight += line.quantity
            line._compute_line_values()
        if cargo_weight > self.vehicle_id.free_capacity:
            raise UserError(_('Choosen cargo is heavier than permissible weight'))


    @api.depends('date_of_departure', 'distance', 'estimated_driving_time')
    def _compute_date_of_departure(self):
        self.predicted_date_arrival = self.date_of_departure
        if self.distance and self.estimated_driving_time:
            self.predicted_date_arrival = self.date_of_departure + timedelta(hours=self.estimated_driving_time)

    def write(self, vals):
        res = super(TransportOrder, self).write(vals)
        if 'place_to' in vals or 'place_from' in vals:
            self._check_distance()
        return res

    @api.model
    def create(self, vals):
        res = super(TransportOrder, self).create(vals)
        res._check_distance()
        return res

    def _check_distance(self):
        self.distance = 0.
        self.estimated_driving_time = ''
        if self.place_to and self.place_from:
            geolocator = Nominatim(user_agent="FleetUMK")
            place_from = geolocator.geocode(f"{self.place_from.street}, {self.place_from.city}, {self.place_from.zip}")
            place_to = geolocator.geocode(f"{self.place_to.street}, {self.place_to.city}, {self.place_to.zip}")
            if place_from and place_to:
                distance = requests.get(f'http://router.project-osrm.org/table/v1/driving/{place_from.longitude},'
                                        f'{place_from.latitude};{place_to.longitude},{place_to.latitude}'
                                        f'?annotations=distance,duration')
                if distance.status_code == 200 and distance.json().get('code', '') == 'Ok':
                    distance = distance.json()
                    self.write({
                        'distance': round(distance['distances'][0][1] / 1000, 2),
                        'estimated_driving_time': round((distance['durations'][0][1] / 60) / 60, 2)
                    })

    @api.depends('cargo_ids', 'cargo_ids.price_unit', 'cargo_ids.quantity', 'cargo_ids.tax_ids', 'cargo_ids.discount')
    def _compute_summary_values(self):
        for order in self:
            net, vat, gross = 0., 0., 0.
            for line in order.cargo_ids:
                net += line.price_net
                vat += line.price_vat
                gross += line.price_total
            order.total_net = net
            order.total_gross = gross
            order.total_vat = vat

    def _get_invoices_count(self):
        for order in self:
            order.invoices_count = order.env['account.move'].search_count([('transport_order_id', '=', order.id)])

    def _get_services_count(self):
        for order in self:
            order.services_count = order.env['fleet.vehicle.log.services'].search_count(
                [('transport_id', '=', order.id)])

    def _create_invoice(self):
        invoice_vals = {
            'ref': self.name,
            'type': 'out_invoice',
            'invoice_origin': self.name,
            'narration': self.internal_note,
            'partner_id': self.partner_id.id,
            'transport_order_id': self.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [],
        }
        for line in self.cargo_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'name': line.label,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom_id.id,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))
        return self.env['account.move'].create(invoice_vals)

    def _check_cargo_status(self):
        for order in self.env['transport.order'].search(
                [('state', '=', 'confirmed'), ('date_of_departure', '!=', False)]):
            if order.date_of_departure <= datetime.now():
                order.write({'state': 'on_way'})

    def confirm_cargo(self):
        for order in self:
            taxes_in_order = []
            for line in order.cargo_ids:
                if line.tax_ids.name in taxes_in_order:
                    raise UserError(_('Diffrent taxes in cargo lines!'))
                else:
                    taxes_in_order.append(line.tax_ids.name)
            if order.invoices_count == 0:
                order._create_invoice()
            order.write({'state': 'confirmed'})

    def end_cargo(self):
        return {
            'name': _('End cargo'),
            'view_type': 'form',
            'res_model': 'end.cargo.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_transport_id': self.id, 'default_vehicle_id': self.vehicle_id.id},
            'target': 'new'
        }

    def cancel_cargo(self):
        for order in self:
            order.write({'state': 'cancel'})

    def back_to_planning(self):
        for order in self:
            order.write({'state': 'planning'})

    def open_invoices(self):
        return {
            'name': _('Invoices'),
            'domain': [('transport_order_id', '=', self.id)],
            'view_type': 'tree',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {}
        }

    def open_services(self):
        return {
            'name': _('Services'),
            'domain': [('transport_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'fleet.vehicle.log.services',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def action_email_send(self):
        self.ensure_one()
        template_id = self.env.ref('dm_flota.dm_flota_mail_template_confirmed_order').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'transport.order', self.ids[0])
        ctx = {
            'default_model': 'transport.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


#dodac
#1. modele aut dostwczych w fleet vehicle model
#2. dodac auta
#3. doac produkty uslugi dla towaru
#4. dodac produkty uslugi dla warsztatu
#5. dodac pojazdy
#6. dodac kierowcow
#7. dodac transporty