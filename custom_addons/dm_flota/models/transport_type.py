# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TransportType(models.Model):
    _name = 'transport.type'
    _description = 'Transport type model'

    name = fields.Char(required=True)
