# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IoniaGestion(models.Model):
    _name = "ionia.gestion"
    _description = "Actividad de gestión de flota en pozos"
    _order = "fecha desc"

    name = fields.Char(string="Actividad", compute="_compute_name", store=True)
    flota_id = fields.Many2one("fleet.vehicle", string="Equipo (flota)")
    pozo_id = fields.Many2one("ionia.pozo", string="Pozo")
    fecha = fields.Datetime(string="Fecha", default=fields.Datetime.now)
    tipo_solicitud = fields.Selection(
        [("solicitud", "Solicitud"), ("traslado", "Traslado"),
         ("operacion", "Operación"), ("reporte", "Reporte")],
        string="Tipo de solicitud")
    estado = fields.Selection(
        [("orden_entrega", "Orden de entrega al pozo"), ("en_camino", "En camino"),
         ("ubicado", "Ubicado en el pozo"), ("activo", "Activo"),
         ("retiro", "Retiro del pozo")],
        string="Estado de la actividad")
    es_falla = fields.Boolean(string="Reporte de falla")
    falla_desc = fields.Text(string="Descripción de la falla")
    notas = fields.Text(string="Observaciones")

    @api.depends("flota_id", "pozo_id")
    def _compute_name(self):
        for r in self:
            plate = r.flota_id.license_plate or "Actividad"
            r.name = "%s @ %s" % (plate, r.pozo_id.name or "-")
