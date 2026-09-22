# Ionia Conpronorte — módulo instalable

Empaqueta los ajustes de la demo Conpronorte (antes aplicados por RPC "estilo Studio")
como un **addon de Odoo 19 instalable**, con código Python y vistas XML.

## Qué incluye
- **Pozo** (`ionia.pozo`): cliente, flota asignada (1 equipo = 1 pozo), contrato de
  alquiler, economía en **USD + Bs** (ingreso/costo/margen/rentabilidad, semáforo),
  estado automático (falla/mantenimiento → En pausa) y estado de mantenimiento.
- **Gestión** (`ionia.gestion`): actividad de flota en pozos (tipo de solicitud,
  estado, reporte de falla).
- **Inventario económico** (`ionia.inv.panel`): tablero KPI con USD (prioridad) + Bs.
- **Mantenimiento**: órdenes con pozo, horas de uso, **próximo mantenimiento** (por
  plazo de horas) y **consumo de repuestos** que descuenta stock y suma el costo.
- **Documentos**: `total_usd` (Total en divisa) en presupuestos/compras/facturas.
- **Flota**: campo Pozo en el equipo.
- Menús/apps con icono y seguridad para usuarios internos.

## Instalar
1. Copiar la carpeta `ionia_conpronorte/` al `addons_path` de la instancia
   (en CloudPepper, por el panel Git / carpeta de addons personalizados).
2. Reiniciar Odoo → **Apps** → *Actualizar lista de aplicaciones*.
3. Instalar **"Ionia Conpronorte"**.

## Notas
- Usa nombres de modelo **limpios** (`ionia.*`), independientes de los modelos `x_*`
  que la demo creó por RPC. Es un módulo para **instalación limpia**.
- Para **migrar** la demo actual (datos en `x_pozo`, `x_gestion`, etc.) a estos
  modelos hay que mapear los datos — es un paso aparte (los scripts RPC del repo
  siguen sirviendo para la instancia actual).
- Depende de: `fleet`, `maintenance`, `sale`, `purchase`, `account`, `stock`.
- Los `xmlid` heredados de Mantenimiento (`maintenance.hr_equipment_view_form`,
  `maintenance.hr_equipment_request_view_form`) son los clásicos; si tu versión de
  Odoo usa otros, ajusta `views/maintenance_views.xml`.
