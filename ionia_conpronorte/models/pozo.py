# -*- coding: utf-8 -*-
from odoo import api, fields, models


def _bs_factor(env):
    """Bs por 1 USD = 1 / (tasa USD por 1 Bs)."""
    usd = env.ref("base.USD", raise_if_not_found=False)
    return (1.0 / usd.rate) if (usd and usd.rate) else 0.0


class IoniaPozo(models.Model):
    _name = "ionia.pozo"
    _description = "Pozo"
    _order = "name"

    name = fields.Char(string="Nombre del pozo", required=True)
    partner_id = fields.Many2one(
        "res.partner", string="Cliente", domain="[('is_company','=',True)]")
    partner_vat = fields.Char(related="partner_id.vat", string="RIF", readonly=True)
    partner_phone = fields.Char(related="partner_id.phone", string="Teléfono", readonly=True)
    partner_email = fields.Char(related="partner_id.email", string="Correo", readonly=True)

    flota_ids = fields.One2many("fleet.vehicle", "pozo_id", string="Flota asignada")

    contrato_ref = fields.Char(string="Referencia de contrato")
    contrato_inicio = fields.Date(string="Inicio de contrato")
    contrato_fin = fields.Date(string="Fin de contrato")
    contrato_monto = fields.Float(string="Monto de alquiler")

    # Economía (prioridad divisa USD; Bs a tasa viva)
    capital_ingreso = fields.Float(string="Capital de ingreso (USD)")
    costo_operativo = fields.Float(string="Otros costos operativos (USD)")
    costo_mant = fields.Float(string="Costo de mantenimiento (USD)",
                              compute="_compute_costos")
    costo_total = fields.Float(string="Costo total (USD)", compute="_compute_costos")
    margen = fields.Float(string="Margen (USD)", compute="_compute_costos")
    margen_pct = fields.Float(string="Rentabilidad %", compute="_compute_costos")
    semaforo = fields.Selection(
        [("alta", "Alta"), ("media", "Media"), ("baja", "Baja")],
        string="Rentabilidad", compute="_compute_costos")
    ingreso_bs = fields.Float(string="Ingreso (Bs)", compute="_compute_bs")
    costo_bs = fields.Float(string="Costo (Bs)", compute="_compute_bs")
    margen_bs = fields.Float(string="Margen (Bs)", compute="_compute_bs")

    finalizado = fields.Boolean(string="Finalizado")
    estado = fields.Selection(
        [("activo", "Activo"), ("pausa_mant", "En pausa por mantenimiento"),
         ("finalizado", "Finalizado")],
        string="Estado", compute="_compute_estado", store=True)
    mant_estado = fields.Char(string="Estado de mantenimiento", compute="_compute_mant_estado")

    # ------- helpers -------
    def _maint_equipment(self):
        """Equipos de Mantenimiento que corresponden a la flota del pozo
        (se cruzan por la matrícula/código contenido en el nombre del equipo)."""
        self.ensure_one()
        plates = [v.license_plate for v in self.flota_ids if v.license_plate]
        if not plates:
            return self.env["maintenance.equipment"]
        dom = ["|"] * (len(plates) - 1) + [("name", "ilike", p) for p in plates]
        return self.env["maintenance.equipment"].search(dom)

    def _open_requests(self):
        self.ensure_one()
        eqs = self._maint_equipment()
        if not eqs:
            return self.env["maintenance.request"]
        reqs = self.env["maintenance.request"].search([("equipment_id", "in", eqs.ids)])
        return reqs.filtered(lambda q: not (q.stage_id and q.stage_id.done))

    # ------- computes -------
    @api.depends("flota_ids", "capital_ingreso", "costo_operativo")
    def _compute_costos(self):
        for r in self:
            cm = sum(e.coste_mant_acum or 0.0 for e in r._maint_equipment()) \
                if hasattr(self.env["maintenance.equipment"], "coste_mant_acum") else 0.0
            r.costo_mant = cm
            r.costo_total = cm + (r.costo_operativo or 0.0)
            r.margen = (r.capital_ingreso or 0.0) - r.costo_total
            r.margen_pct = (r.margen / r.capital_ingreso * 100.0) if r.capital_ingreso else 0.0
            r.semaforo = "alta" if r.margen_pct >= 50 else ("media" if r.margen_pct >= 20 else "baja")

    @api.depends("capital_ingreso", "costo_operativo", "flota_ids")
    def _compute_bs(self):
        f = _bs_factor(self.env)
        for r in self:
            r.ingreso_bs = (r.capital_ingreso or 0.0) * f
            r.costo_bs = (r.costo_total or 0.0) * f
            r.margen_bs = (r.margen or 0.0) * f

    @api.depends("flota_ids")
    def _compute_mant_estado(self):
        for r in self:
            openq = r._open_requests()
            if openq.filtered(lambda q: q.maintenance_type == "corrective"):
                r.mant_estado = "Alerta de falla"
            elif openq.filtered(lambda q: q.maintenance_type == "preventive"):
                r.mant_estado = "Solicitud de mantenimiento"
            elif openq:
                r.mant_estado = "En mantenimiento"
            else:
                r.mant_estado = "Sin alertas"

    @api.depends("flota_ids", "finalizado")
    def _compute_estado(self):
        for r in self:
            if r.finalizado:
                r.estado = "finalizado"
            elif r.mant_estado in ("Alerta de falla", "En mantenimiento"):
                r.estado = "pausa_mant"
            else:
                r.estado = "activo"
