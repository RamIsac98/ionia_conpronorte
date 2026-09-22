# -*- coding: utf-8 -*-
{
    "name": "Ionia Conpronorte — Pozos, Gestión, Flota y Rentabilidad",
    "version": "19.0.1.0.0",
    "summary": "Módulos de la operación Conpronorte: pozos, gestión de flota, "
               "mantenimiento por horas/repuestos y rentabilidad por pozo (USD/Bs).",
    "author": "Ionia Solutions",
    "website": "https://ioniasolutions.com",
    "license": "LGPL-3",
    "category": "Services/Oilfield",
    "depends": [
        "base", "mail", "product", "stock", "fleet", "maintenance",
        "sale", "purchase", "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/pozo_views.xml",
        "views/gestion_views.xml",
        "views/inv_panel_views.xml",
        "views/maintenance_views.xml",
        "views/account_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
