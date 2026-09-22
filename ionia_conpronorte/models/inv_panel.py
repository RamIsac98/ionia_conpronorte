# -*- coding: utf-8 -*-
from odoo import api, fields, models

CAT_MANT = "Consumibles Operación"


def _bs_factor(env):
    usd = env.ref("base.USD", raise_if_not_found=False)
    return (1.0 / usd.rate) if (usd and usd.rate) else 0.0


class IoniaInvPanel(models.Model):
    _name = "ionia.inv.panel"
    _description = "Panel económico de pozos"

    name = fields.Char(default="Panel económico de pozos")
    ingreso_global = fields.Float(string="Capital de ingreso global (USD)", compute="_compute_kpis")
    costo_global = fields.Float(string="Capital de costo global (USD)", compute="_compute_kpis")
    margen_global = fields.Float(string="Margen global (USD)", compute="_compute_kpis")
    margen_global_pct = fields.Float(string="Rentabilidad global %", compute="_compute_kpis")
    ingreso_global_bs = fields.Float(string="Ingreso global (Bs)", compute="_compute_kpis")
    costo_global_bs = fields.Float(string="Costo global (Bs)", compute="_compute_kpis")
    margen_global_bs = fields.Float(string="Margen global (Bs)", compute="_compute_kpis")
    n_pozos = fields.Integer(string="Pozos", compute="_compute_kpis")
    n_activos = fields.Integer(string="Pozos activos", compute="_compute_kpis")
    n_pausa = fields.Integer(string="Pozos en pausa", compute="_compute_kpis")
    n_fallas = fields.Integer(string="Fallas abiertas", compute="_compute_kpis")
    stock_valor_mant = fields.Float(string="Valor stock de mantenimiento (Bs)", compute="_compute_kpis")
    gastos_compra_mant = fields.Float(string="Gastos de compra de repuestos (Bs)", compute="_compute_kpis")

    def _compute_kpis(self):
        Pozo = self.env["ionia.pozo"]
        Prod = self.env["product.product"]
        POL = self.env["purchase.order.line"]
        Req = self.env["maintenance.request"]
        f = _bs_factor(self.env)
        for panel in self:
            pozos = Pozo.search([])
            ing = sum(p.capital_ingreso or 0.0 for p in pozos)
            cos = sum(p.costo_total or 0.0 for p in pozos)
            panel.ingreso_global = ing
            panel.costo_global = cos
            panel.margen_global = ing - cos
            panel.margen_global_pct = ((ing - cos) / ing * 100.0) if ing else 0.0
            panel.ingreso_global_bs = ing * f
            panel.costo_global_bs = cos * f
            panel.margen_global_bs = (ing - cos) * f
            panel.n_pozos = len(pozos)
            panel.n_activos = len(pozos.filtered(lambda p: p.estado == "activo"))
            panel.n_pausa = len(pozos.filtered(lambda p: p.estado == "pausa_mant"))
            reqs = Req.search([("maintenance_type", "=", "corrective")])
            panel.n_fallas = len(reqs.filtered(lambda q: not (q.stage_id and q.stage_id.done)))
            prods = Prod.search([("categ_id.name", "=", CAT_MANT)])
            panel.stock_valor_mant = sum((p.qty_available or 0.0) * (p.standard_price or 0.0) for p in prods)
            lines = POL.search([("product_id", "in", prods.ids)])
            panel.gastos_compra_mant = sum(l.price_subtotal or 0.0 for l in lines)
