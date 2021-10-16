# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class TransportOrder(models.Model):
    _name = 'transport.order'
    _inherit = ['mail.thread']
    _description = 'Transport Order model'

    name = fields.Char(required=True)

    partner_id = fields.Many2one('res.partner', required=True)
    place_from = fields.Many2one('transport.place', required=True, track_visibility='onchange')
    place_to = fields.Many2one('transport.place', required=True, track_visibility='onchange')
    # vehicle_id = fields.Many2one('')
    date_of_departure = fields.Datetime(required=True, track_visibility='onchange')
    # estimated_driving_time na podstawie sredniej u kierowcy z jaka zapierdala ;d
    # predicted_date_arrival = fields.Datetime  to bedzie data startu plus przewidywany czas jazdy
    # odleglosc w kilometrach wyliczana
    driver_id = fields.Many2one('hr.employee', required=True, track_visibility='onchange')
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, track_visibility='onchange')
    cargo_ids = fields.One2many('transport.order.line', 'transport_id')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.ref('base.PLN'))
    total_gross = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_net = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_vat = fields.Monetary(compute='_compute_summary_values', readonly=True)
    internal_note = fields.Char()
    state = fields.Selection([('planning', "Planning"), ('confirmed', "Confirmed"), ('on_way', "On the way"),
                              ('delivered', 'Delivered'), ('cancel', 'Cancel')], default='planning', readonly=True, track_visibility='onchange')
    type = fields.Many2one('transport.type')
    invoices_count = fields.Integer(compute='_get_invoices_count')

    @api.onchange('cargo_ids')
    def _onchange_cargo_ids(self):
        for line in self.cargo_ids:
            line._compute_line_values()

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
        for order in self.env['transport.order'].search([('state', '=', 'confirmed'), ('date_of_departure', '!=', False)]):
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

    # @api.constrains('vehicle_id')
    # def _check_vehlice_avaiability(self):
    #     for order in self:
    #         #sprawdz czy nie bedzie w tym czasie dostepny

    # @api.constrains('vehicle_id')
    # def _check_driver_avaiability(self):
    #     for order in self:
    #         #sprawdz czy nie bedzie w tym czasie dostepny

    # w pojazdach liczone srednie zucycie na podstawie tras w jakich bral udzial i ile spalil paliwa
    # jak beda statusy: planowany -> przy zmianie statusu ma sie wystawic faktura ale w fakturach nic nie zmieniac->potwierdzony - > w trasie -> i tutaj trzeba bedzie guzikiem zatwierdzic gdzie wyskoczy wizard do wpisania litrow paliwa i notatki po zakonczeniu trasy i sie zmieni na done
    # zrobic status w hr employee -> czy jest w trasie czy tez nie na podstawie aktualnej daty i czy ma teraz zleceniea

    # jednostka miary musi byc w kg i wtedy bedzie mozna sprawdzac czy wybrany pojazd ma taka ladownosc
    # nie wiem czy ladownosc jest w pojazdach wiec trzeba by bylo ddoac wtedy

    # dodac send by ermail tak jak jest to w sale orderze


