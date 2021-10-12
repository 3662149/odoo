# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TransportOrder(models.Model):
    _name = 'transport.order'
    _description = 'Transport Order model'

    name = fields.Char(required=True)

    partner_id = fields.Many2one('res.partner', required=True)
    place_from = fields.Many2one('transport.place', required=True)
    place_to = fields.Many2one('transport.place', required=True)
    # vehicle_id = fields.Many2one('')
    date_of_departure = fields.Datetime()
    # estimated_driving_time na podstawie sredniej u kierowcy z jaka zapierdala ;d
    # predicted_date_arrival = fields.Datetime  to bedzie data startu plus przewidywany czas jazdy
    # odleglosc w kilometrach wyliczana
    driver = fields.Many2one('hr.employee', required=True)  # przeciazyc dodac pole many2one z lista transport order
    cargo_ids = fields.One2many('transport.order.line', 'transport_id')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.ref('base.PLN'))
    total_gross = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_net = fields.Monetary(compute='_compute_summary_values', readonly=True)
    total_vat = fields.Monetary(compute='_compute_summary_values', readonly=True)
    internal_note = fields.Char()
    state = fields.Selection([('planning', "Planning"), ('confirmed', "Confirmed"), ('on_way', "On the way"),
                              ('delivered', 'Delivered'), ('cancel', 'Cancel')], default='planning', readonly=True)
    type = fields.Many2one('transport.type')

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


    # @api.constrains('vehicle_id')
    # def _check_vehlice_avaiability(self):
    #     for order in self:
    #         #sprawdz czy nie bedzie w tym czasie dostepny

    # na potwierdzeniu statusu nalezy sprawdzic czy liny maja ten sam podatek
    #w pojazdach liczone srednie zucycie na podstawie tras w jakich bral udzial i ile spalil paliwa
    #dodac grupe uprawnien i nadac w widoku prawwa groups="account.group_account_invoice" wtedy jak w fieldie  albow  buttonie jest cos takiego to tylkoz  tytmi uprawnieniami moze
    # jak beda statusy: planowany -> przy zmianie statusu ma sie wystawic faktura ale w fakturach nic nie zmieniac->potwierdzony - > w trasie -> i tutaj trzeba bedzie guzikiem zatwierdzic gdzie wyskoczy wizard do wpisania litrow paliwa i notatki po zakonczeniu trasy i sie zmieni na done
    # zrobic status w hr employee -> czy jest w trasie czy tez nie na podstawie aktualnej daty i czy ma teraz zleceniea