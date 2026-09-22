# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IoniaMaintRepuesto(models.Model):
    _name = "ionia.maint.repuesto"
    _description = "Línea de repuesto de mantenimiento"

    request_id = fields.Many2one(
        "maintenance.request", string="Orden", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product", string="Repuesto", domain="[('type','=','consu')]")
    qty = fields.Float(string="Cantidad", default=1.0)
    subtotal = fields.Float(string="Costo", compute="_compute_subtotal")
    consumido = fields.Boolean(string="Consumido (stock descontado)", readonly=True)
    move_id = fields.Many2one("stock.move", string="Movimiento", readonly=True)

    @api.depends("product_id", "qty")
    def _compute_subtotal(self):
        for r in self:
            r.subtotal = (r.product_id.standard_price or 0.0) * (r.qty or 0.0)
