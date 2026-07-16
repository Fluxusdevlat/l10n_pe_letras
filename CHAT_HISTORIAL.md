# HISTORIAL DE SESIÓN - Módulo l10n_pe_letras

**Fecha:** 15 Julio 2026
**Cliente:** Fluxus Lat (Perú) - Odoo 19 Enterprise
**Proyecto:** https://github.com/Fluxusdevlat/fluxus (rama `desarrollos`)
**Herramienta:** opencode CLI

---

## 1. REQUERIMIENTO DEL CLIENTE

Implementación personalizada en Odoo para empresa peruana de producción, comercialización y logística. Se acordó dividir en **módulos independientes**:

| Módulo | Estado |
|--------|--------|
| `l10n_pe_letras` | ✅ **Creado y desplegado** |
| `l10n_pe_credit_lines` | ❌ Pendiente |
| `l10n_pe_cavali_factoring` | ❌ Pendiente |
| `l10n_pe_treasury` | ❌ Pendiente |
| `l10n_pe_reports` | ❌ Pendiente |

---

## 2. MÓDULO CREADO: l10n_pe_letras

### Estructura

```
l10n_pe_letras/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── letra.py              # Letra de Cambio + líneas factura
│   ├── letra_planilla.py     # Planilla bancaria
│   ├── letra_protesto.py     # Protestos con gastos
│   ├── letra_renovacion.py   # Renovaciones con intereses
│   ├── credit_group.py       # Grupo empresarial + crédito compartido
│   ├── res_partner.py        # Bloqueo comercial en partner
│   ├── account_move.py       # Campos CAVALI/Factoring en factura
│   └── sale_order.py         # Bloqueo al confirmar pedido
├── views/ (9 XML)
│   ├── letra_views.xml, planilla, protesto, renovacion
│   ├── credit_group_views.xml
│   ├── res_partner_views.xml (herencia)
│   ├── account_move_views.xml (herencia)
│   ├── sale_order_views.xml (herencia)
│   └── menu_views.xml
├── wizards/
│   ├── generar_letras_wizard.py    # Facturas → Letras
│   └── renovacion_wizard.py        # Renovar con intereses
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/letra_sequence.xml
├── reports/letra_templates.xml     # PDF Letra + Planilla
└── static/description/icon.png
```

### Funcionalidades Implementadas

**Gestión de Letras**
- Registro manual y automático desde facturas
- 8 estados: borrador, enviada, firmada, en banco, protestada, cancelada, renovada, pagada
- Asociación flexible: N facturas ↔ 1 letra, o 1 factura ↔ N letras
- Impresión PDF formato letra de cambio

**Protestos**
- Registro con fecha, monto, gastos y costas
- Cambia estado de letra a "Protestada"
- Regularización con fecha y tipo

**Renovaciones**
- Nueva letra (canje) con intereses y gastos
- Historial: letra origen ↔ letra destino

**Planillas Bancarias**
- Agrupa letras por banco
- Estados: borrador, enviada, confirmada
- Impresión planilla consolidada + letras individuales

**Grupos Empresariales**
- Varias empresas comparten línea de crédito
- Cálculo automático: crédito usado = facturas pendientes + pedidos sin facturar + letras emitidas

**Bloqueo Comercial**
- Cliente con letras protestadas → bloqueado para nuevas ventas
- Bloqueo se valida al confirmar pedido (sale.order.action_confirm)

**Integración Facturas**
- Estado: sin letra / parcial / total
- Campos preparados para CAVALI y Factoring

### Modelos Creados

| Model | Descripción |
|-------|-------------|
| `l10n.pe.letra` | Letra de cambio |
| `l10n.pe.letra.line` | Factura asociada a letra |
| `l10n.pe.letra.planilla` | Planilla de letras para banco |
| `l10n.pe.letra.protesto` | Protesto de letra |
| `l10n.pe.letra.renovacion` | Renovación |
| `l10n.pe.credit.group` | Grupo empresarial |
| `l10n.pe.letra.generate.wizard` | Wizard generación |
| `l10n.pe.letra.renovacion.wizard` | Wizard renovación |

### Dependencias

`base`, `account`, `sale`, `l10n_pe`

### Moneda

La compañía se configuró con **PEN (Soles)**.

---

## 3. DESPLIEGUE

### Local (Docker)
```bash
# Contenedores
docker run -d -p 5432:5432 --name db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo postgres:16
docker run -d -p 8069:8069 --name odoo19 --link db:db \
  -v ~/Downloads/odoo19/custom_addons:/mnt/extra-addons \
  -v ~/Downloads/odoo19/odoo.conf:/etc/odoo/odoo.conf \
  odoo:19.0
# URL: http://localhost:8069
```

### Odoo.sh
```bash
# El módulo está en Fluxusdevlat/fluxus rama desarrollos
# Para actualizar:
cd fluxus_repo
git pull
cp -r ../l10n_pe_letras/ .
git add .
git commit -m "actualización"
git push
# Odoo.sh reconstruye automáticamente
```

### BD Local usada
- Nombre: `fluxuslat_test`
- Master password: `admin`

---

## 4. PENDIENTE COMPLETO POR REQUERIMIENTO

### 4.1 Créditos y Cobranzas (módulo l10n_pe_letras)

| REQ | Descripción | Estado | Plan |
|-----|-------------|--------|------|
| CYC-9 | Anticipos mediante letras de canje | ⚠️ Parcial | Crear modelo `l10n.pe.letra.anticipo` con: partner, letra_id, monto, saldo_aplicado, facturas_ids. Wizard para aplicar anticipo a facturas |
| CYC-13 | Gestión CAVALI | ⚠️ Parcial | Modelo `l10n.pe.cavali.operation`: partner, factura_id, monto_negociado, fecha, estado (negociada/en_proceso/cancelada/pagada), entidad_financiera. Reporte planilla CAVALI |
| CYC-14 | Factoring | ⚠️ Parcial | Modelo `l10n.pe.factoring`: factura_id, entidad_factor, fecha_cesion, monto, estado, fecha_liquidacion. Trazabilidad completa |
| CYC-15 | Reporte cartera financiera | ❌ | Reporte consolidado (QWeb) mostrando letras + anticipos + CAVALI + factoring por cliente, con saldos vigentes |

### 4.2 Tesorería (nuevo módulo: l10n_pe_treasury)

| REQ | Descripción | Plan |
|-----|-------------|------|
| TES-1 | Flujo de caja proyectado | Modelo `l10n.pe.cash.flow.item`: fecha, tipo (ingreso/egreso), monto, cuenta_bancaria, origen (factura/letra). Reporte QWeb con proyección diaria/semanal/mensual |
| TES-2 | Programación de pagos | Modelo `l10n.pe.payment.schedule`: proveedor, factura_ids, letra_canje_id, fecha_vencimiento, monto, prioridad, estado. Vista kanban por estado |
| TES-3 | Caja chica y rendiciones | Modelo `l10n.pe.petty.cash`: fondo_asignado, responsable, saldo_actual. Modelo `l10n.pe.petty.cash.expense`: monto, concepto, comprobante, fecha. Wizard rendición con saldos |
| TES-4 | Préstamos bancarios (interés variable) | Modelo `l10n.pe.loan`: banco, monto, tasa_interes, tipo_tasa (diaria/semanal/mensual), fecha_inicio, cuotas. Modelo `l10n.pe.loan.installment`: nro_cuota, fecha, capital, interes, saldo. Cálculo de interés diario configurable |
| TES-5 | Pagarés | Modelo `l10n.pe.promissory.note`: similar a letra pero para proveedores. nro_pagare, banco, monto, fecha_emision, fecha_vencimiento, estado |
| TES-6 | Leasing | Modelo `l10n.pe.leasing.contract`: entidad, activo_id, monto_total, cuotas, tasa, fecha_inicio. Modelo `l10n.pe.leasing.installment`: cronograma de cuotas |
| TES-7 | Integración bancaria (Host to Host) | Modelo `l10n.pe.bank.integration`: banco, tipo_servicio, config_conexion (API/archivo). Generación de archivos planos según formato de cada banco. Programar tarea cron para envío/recepción |

### 4.3 Ventas (módulo l10n_pe_letras)

| REQ | Descripción | Estado | Plan |
|-----|-------------|--------|------|
| VTA-2 | Alerta preventiva de crédito | ❌ | En `sale_order.py`: al confirmar pedido, si el crédito disponible queda < 20% del límite, mostrar warning/wizard de confirmación antes de continuar. Añadir campo `credit_usage_pct` como badge en la vista |

### 4.4 Reportes

| REQ | Descripción | Plan |
|-----|-------------|------|
| REP-1 | Proyección cobranzas semanal | Reporte QWeb agrupando por semana: cliente, documentos, vencimientos, montos, banco |
| REP-2 | Estado de cuenta por cliente | Reporte QWeb: facturas + letras + anticipos + NC + pagos + saldo. Filtro por cliente y fechas |
| REP-3 | Estado de cuenta por grupo empresarial | REP-2 pero agrupado por `credit_group_id` |
| REP-4 | Reporte líneas de crédito | Tabla: cliente/grupo, límite, usado, disponible, % uso |
| REP-5 | Reporte de letras | Listado completo con filtros: estado, cliente, banco, fechas |
| REP-6 | Planilla facturas CAVALI | Reporte similar a planilla de letras pero para CAVALI |
| REP-7 | Facturas por letra | Vista desde la letra (ya funcional) + botón imprimir |
| REP-8 | Letras por factura | Vista desde la factura (ya funcional) + botón imprimir |
| REP-9 | Kardex valorizado | Modelo/extensión de `stock.move` para mostrar entradas/salidas/saldos con costos. Reporte QWeb con filtros: producto, categoría, almacén, fechas |
| REP-10 | Dashboard gerencial | Personalizar dashboard existente para incluir indicadores de letras (cartera, protestos, vencidos) |
| REP-11 | Clientes bloqueados | Vista tree/list filtrable con `commercial_blocked = True` |
| REP-12 | Historial de protestos | Vista tree de protestos agrupados por cliente, con filtro por fechas |

---

## 5. PLAN DE IMPLEMENTACIÓN (MÓDULOS PENDIENTES)

### Módulo 1: `l10n_pe_letras` - Completar
**Prioridad:** Media | **Esfuerzo estimado:** 2-3 días

- [ ] Completar lógica CAVALI (CYC-13)
- [ ] Completar lógica Factoring (CYC-14)
- [ ] Anticipos con letras de canje (CYC-9)
- [ ] Alerta preventiva crédito (VTA-2)
- [ ] Reporte cartera consolidada (CYC-15)
- [ ] Reporte de letras (REP-5)
- [ ] Reporte clientes bloqueados (REP-11)
- [ ] Historial protestos (REP-12)
- [ ] Dashboard indicadores letras (REP-10)
- [ ] Corregir warnings: `_sql_constraints`, `tracking`

### Módulo 2: `l10n_pe_treasury` - Tesorería
**Prioridad:** Alta | **Esfuerzo estimado:** 5-7 días

- [ ] TES-3: Caja chica y rendiciones (modelo + vistas)
- [ ] TES-4: Préstamos bancarios con interés variable
- [ ] TES-5: Pagarés
- [ ] TES-6: Leasing
- [ ] TES-1: Flujo de caja proyectado
- [ ] TES-2: Programación de pagos
- [ ] TES-7: Integración bancaria Host to Host

### Módulo 3: `l10n_pe_reports` - Reportes
**Prioridad:** Media | **Esfuerzo estimado:** 4-5 días

- [ ] REP-2: Estado de cuenta por cliente
- [ ] REP-3: Estado de cuenta por grupo empresarial
- [ ] REP-4: Reporte líneas de crédito
- [ ] REP-1: Proyección cobranzas
- [ ] REP-9: Kardex valorizado
- [ ] REP-6: Planilla CAVALI
- [ ] REP-7, REP-8: Reportes facturas/letras

### Módulo 4: `l10n_pe_cavali_factoring` - CAVALI y Factoring
**Prioridad:** Media | **Esfuerzo estimado:** 2-3 días

- [ ] Operaciones CAVALI con estados
- [ ] Cesión de facturas (Factoring)
- [ ] Planilla CAVALI imprimible
- [ ] Trazabilidad hasta liquidación

---

## 6. DEPENDENCIAS ENTRE MÓDULOS

```
l10n_pe_letras (base)
    │
    ├── l10n_pe_credit_lines (usa credit_group)
    │
    ├── l10n_pe_cavali_factoring (usa account_move extendido)
    │
    ├── l10n_pe_treasury (independiente, usa account)
    │
    └── l10n_pe_reports (depende de todos)
```

---

## 7. DATOS DE CONEXIÓN PARA PRÓXIMA SESIÓN

### GitHub

| Dato | Valor |
|------|-------|
| Repo principal (Odoo.sh) | `Fluxusdevlat/fluxus` |
| Rama | `desarrollos` |
| URL HTTPS | `https://github.com/Fluxusdevlat/fluxus.git` |
| Ruta local del clone | `/Users/javierascue/Downloads/PROYECTOS/PRUEBAS/CURPISCO/fluxus_repo` |
| Autenticación | HTTPS (sin SSH). Token GitHub: `(generar en Settings → Developer settings → Tokens classic → repo)` |
| Repo secundario (módulo solo) | `Javicheti/l10n_pe_letras` (público) |
| Módulo en GitHub | https://github.com/Fluxusdevlat/fluxus/tree/desarrollos/l10n_pe_letras |

### Odoo.sh

| Dato | Valor |
|------|-------|
| Proyecto | `fluxusdevlat-fluxus` |
| URL | https://www.odoo.sh/ (proyecto fluxusdevlat-fluxus) |
| Rama producción | `Producción` (19.0) |
| Rama pruebas | `Pruebas` (19.0) |
| Rama desarrollo | `desarrollos` (19.0) |

### Docker Local

| Dato | Valor |
|------|-------|
| Contenedor Odoo | `odoo19` |
| Contenedor DB | `db` |
| BD nombre | `fluxuslat_test` |
| Master password | `admin` |
| Puerto | `localhost:8069` |
| Ruta addons en contenedor | `/mnt/extra-addons/l10n_pe_letras` |
| Ruta addons local | `~/Downloads/odoo19/custom_addons/l10n_pe_letras` |

### Módulo Local

| Dato | Valor |
|------|-------|
| Ruta fuente principal | `/Users/javierascue/Downloads/PROYECTOS/PRUEBAS/CURPISCO/l10n_pe_letras` |
| ZIP | `/Users/javierascue/Downloads/PROYECTOS/PRUEBAS/CURPISCO/l10n_pe_letras.zip` |
| Documentación | `/Users/javierascue/Downloads/PROYECTOS/PRUEBAS/CURPISCO/l10n_pe_letras/CHAT_HISTORIAL.md` |

### Comandos Rápidos

```bash
# Actualizar en Odoo.sh
cd /Users/javierascue/Downloads/PROYECTOS/PRUEBAS/CURPISCO/fluxus_repo
git pull
cp -r ../l10n_pe_letras/ .
git add .
git commit -m "actualización"
GIT_TERMINAL_PROMPT=0 git push

# Actualizar en Docker local
docker cp l10n_pe_letras/. odoo19:/mnt/extra-addons/l10n_pe_letras/
docker restart odoo19

# Forzar upgrade en BD local
docker exec odoo19 python3 -c "
import odoo
from odoo.modules.registry import Registry
r = Registry.new('fluxuslat_test')
with r.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    mod = env['ir.module.module'].search([('name','=','l10n_pe_letras')], limit=1)
    mod.button_immediate_upgrade()
    cr.commit()
"
```

### Notas Técnicas Odoo 19

| Cambio respecto a Odoo 16/17 | Cómo se usa ahora |
|------------------------------|-------------------|
| `<tree>` | `<list>` |
| `states="draft"` en botones | `invisible="state != 'draft'"` |
| `attrs="{'invisible': ...}"` | `invisible="expresion"` |
| `<report>` tag | `<record model="ir.actions.report">` |
| `@api.model def create(self, vals)` | `@api.model_create_multi def create(self, vals_list)` |
| `<main>` en reportes QWeb | Obligatorio envolver en `<main>` |
| `_sql_constraints` | `models.Constraint` (warning, funciona igual) |
| `tracking=True` en Selection | No soportado, quitar |
