# -*- coding: utf-8 -*-
from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    pozo_id = fields.Many2one("ionia.pozo", string="Pozo")
