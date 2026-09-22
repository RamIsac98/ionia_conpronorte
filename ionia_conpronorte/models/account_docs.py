# -*- coding: utf-8 -*-
from odoo import api, fields, models


def _usd_rate(env):
    usd = env.ref("base.USD", raise_if_not_found=False)
    return usd.rate if (usd and usd.rate) else 0.0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_usd = fields.Float(string="Total en divisa (USD $)", compute="_compute_total_usd")

    @api.depends("amount_total")
    def _compute_total_usd(self):
        f = _usd_rate(self.env)
        for r in self:
            r.total_usd = (r.amount_total or 0.0) * f


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_usd = fields.Float(string="Total en divisa (USD $)", compute="_compute_total_usd")

    @api.depends("amount_total")
    def _compute_total_usd(self):
        f = _usd_rate(self.env)
        for r in self:
            r.total_usd = (r.amount_total or 0.0) * f


class AccountMove(models.Model):
    _inherit = "account.move"

    total_usd = fields.Float(string="Total en divisa (USD $)", compute="_compute_total_usd")

    @api.depends("amount_total")
    def _compute_total_usd(self):
        f = _usd_rate(self.env)
        for r in self:
            r.total_usd = (r.amount_total or 0.0) * f
