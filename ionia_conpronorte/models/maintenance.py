# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    # Seguimiento por horas de trabajo (horómetro) y costo acumulado.
    horas_actual = fields.Float(string="Horómetro (horas del ciclo)")
    horas_intervalo = fields.Float(string="Plazo de mantenimiento (horas)", default=250.0)
    horas_por_dia = fields.Float(string="Horas de uso por día", default=12.0)
    coste_mant_acum = fields.Float(string="Costo de mantenimiento acumulado", readonly=True)


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    pozo_id = fields.Many2one("ionia.pozo", string="Pozo (ubicación)",
                              compute="_compute_pozo", store=True)
    horas_uso = fields.Float(related="equipment_id.horas_actual", string="Horas de uso", readonly=True)
    coste_total = fields.Float(string="Costo del mantenimiento", readonly=True)
    nota_repuestos = fields.Text(string="Nota de cambio de repuestos")
    repuesto_line_ids = fields.One2many("ionia.maint.repuesto", "request_id", string="Repuestos")
    fecha_prox_mant = fields.Date(string="Próximo mantenimiento", compute="_compute_fecha_prox")

    @api.depends("equipment_id")
    def _compute_pozo(self):
        Fleet = self.env["fleet.vehicle"]
        for r in self:
            pozo = False
            if r.equipment_id and r.equipment_id.name:
                for v in Fleet.search([("pozo_id", "!=", False)]):
                    if v.license_plate and v.license_plate in r.equipment_id.name:
                        pozo = v.pozo_id.id
                        break
            r.pozo_id = pozo

    @api.depends("equipment_id", "equipment_id.horas_actual",
                 "equipment_id.horas_intervalo", "equipment_id.horas_por_dia")
    def _compute_fecha_prox(self):
        for r in self:
            eq = r.equipment_id
            r.fecha_prox_mant = False
            if eq and eq.horas_intervalo > 0:
                restantes = max(eq.horas_intervalo - (eq.horas_actual or 0.0), 0.0)
                por_dia = eq.horas_por_dia or 12.0
                dias = int(restantes / por_dia) if por_dia else 0
                r.fecha_prox_mant = date.today() + timedelta(days=dias)

    def _consumo_location(self):
        loc = self.env["stock.location"].search(
            [("name", "=", "Consumo de Mantenimiento")], limit=1)
        if not loc:
            loc = self.env["stock.location"].create(
                {"name": "Consumo de Mantenimiento", "usage": "inventory"})
        return loc

    def action_consumir_repuestos(self):
        """Descuenta del stock los repuestos y suma su costo al equipo/orden."""
        Move = self.env["stock.move"]
        MoveLine = self.env["stock.move.line"]
        dest = self._consumo_location()
        wh = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1)
        src = wh.lot_stock_id if wh else False
        for req in self:
            if not src:
                raise UserError("No hay almacén principal configurado.")
            total = 0.0
            for line in req.repuesto_line_ids.filtered(lambda l: not l.consumido and l.product_id):
                move = Move.create({
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                    "product_uom": line.product_id.uom_id.id,
                    "location_id": src.id,
                    "location_dest_id": dest.id,
                    "origin": "Consumo mant. %s" % (req.name or ""),
                })
                move._action_confirm()
                move._action_assign()
                if move.move_line_ids:
                    move.move_line_ids.write({"quantity": line.qty})
                else:
                    MoveLine.create({
                        "move_id": move.id, "product_id": line.product_id.id,
                        "quantity": line.qty, "location_id": src.id,
                        "location_dest_id": dest.id})
                move.picked = True
                move._action_done()
                line.write({"consumido": True, "move_id": move.id})
                total += line.subtotal or 0.0
            if total:
                req.coste_total = (req.coste_total or 0.0) + total
                if req.equipment_id:
                    req.equipment_id.coste_mant_acum = (
                        req.equipment_id.coste_mant_acum or 0.0) + total
        return True
