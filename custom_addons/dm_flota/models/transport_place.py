# -*- coding: utf-8 -*-
from odoo import models, fields


class TransportPlace(models.Model):
    _name = 'transport.place'
    _description = 'Transport Place model'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    country_id = fields.Many2one('res.country')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s - %s' % (rec.name, rec.partner_id.name, rec.country_id.name)))
        return result
