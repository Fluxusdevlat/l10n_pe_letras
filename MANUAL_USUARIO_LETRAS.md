# MANUAL DE USUARIO Y OPERATIVO
## MÓDULO DE LETRAS DE CAMBIO Y COBRANZAS — PERÚ
### Curpisco · Odoo 19

> **Versión del módulo documentada:** `19.0.1.40.0`
> **Compañía:** CURPISCO S.A.C. · Moneda: PEN (S/)
> **Última actualización:** Septiembre 2026

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción y Glosario](#1-introducción-y-glosario)
2. [Accesos y Menú del Módulo](#2-accesos-y-menú-del-módulo)
   - [2.1 Descripción de cada Opción del Menú](#21-descripción-de-cada-opción-del-menú)
3. [Configuración Inicial y Datos Maestros](#3-configuración-inicial-y-datos-maestros)
   - [3.1 Ficha del Cliente](#31-ficha-del-cliente-respartner)
   - [3.2 Grupos Empresariales](#32-grupos-empresariales-l10npecreditgroup)
   - [3.3 Parámetros Globales (Ajustes)](#33-parámetros-globales-ajustes)
4. [Emisión de Letras de Cambio](#4-emisión-de-letras-de-cambio)
   - [4.1 Generación Automática desde Facturas](#41-generación-automática-desde-facturas)
   - [4.2 Registro Manual (Formulario Campo por Campo)](#42-registro-manual-formulario-campo-por-campo)
   - [4.3 Reglas de Selección de Facturas](#43-reglas-de-selección-de-facturas)
5. [Ciclo de Vida de la Letra (Paso a Paso)](#5-ciclo-de-vida-de-la-letra-paso-a-paso)
6. [Modalidad Cabal](#6-modalidad-cabal)
7. [Planillas de Envío al Banco](#7-planillas-de-envío-al-banco)
8. [Protesto de Letras](#8-protesto-de-letras)
9. [Renovación de Letras](#9-renovación-de-letras)
10. [Proyección Semanal de Cobranza](#10-proyección-semanal-de-cobranza)
11. [Envío por Email y Exportación Excel](#11-envío-por-email-y-exportación-excel)
12. [Reglas de Negocio y Bloqueos](#12-reglas-de-negocio-y-bloqueos)
13. [Catálogo de Reportes](#13-catálogo-de-reportes)
14. [Alertas y Automatizaciones](#14-alertas-y-automatizaciones)
15. [Seguridad y Roles](#15-seguridad-y-roles)
16. [Apéndice A — Novedades de esta Versión](#16-apéndice-a--novedades-de-esta-versión)
17. [Apéndice B — Checklist de Verificación](#17-apéndice-b--checklist-de-verificación)

---

## 1. INTRODUCCIÓN Y GLOSARIO

El módulo **`l10n_pe_letras`** gestiona el ciclo completo de cobranza con **Letras de Cambio al Descuento Bancario** y operaciones **Cabal**, adaptado a la operación peruana de Curpisco.

### Glosario de términos

| Término | Significado |
|---|---|
| **Letra de cambio** | Documento de crédito que el cliente firma prometiendo pagar un importe en una fecha. Curpisco lo descuenta en el banco para cobrar por adelantado. |
| **Girador** | Quien emite la letra (Curpisco). |
| **Aceptante** | El cliente que firma y sella la letra. |
| **Descuento / Canje** | Venta de la letra al banco (BCP, Scotiabank, BBVA) para recibir el dinero antes del vencimiento. |
| **Planilla** | Documento que agrupa varias letras y se presenta al banco para su descuento. |
| **Protesto** | Cuando el cliente no paga al vencimiento, el banco debita el importe a Curpisco y la letra queda "protestada". |
| **Renovación** | Pago parcial de una letra y generación de una nueva por el saldo (siempre a 30 días). |
| **Cabal** | Modalidad para clientes especiales: la factura se canjea al 100% en el banco (telecrédito) sin letra ni firma física. |
| **Grupo Empresarial** | Conjunto de razones sociales que comparten una **misma línea de crédito**. |

---

## 2. ACCESOS Y MENÚ DEL MÓDULO

El módulo tiene una aplicación propia llamada **Letras de Cambio** (ícono en el menú de aplicaciones) con esta estructura:

```
Letras de Cambio
├── Operaciones
│   ├── Letras de Cambio              (listado general; Lista/Kanban/Calendario/Pivot/Gráfico)
│   ├── Operaciones Cabal             (listado filtrado por tipo Cabal)
│   ├── Planillas                     (planillas de envío al banco)
│   └── Generar Letras desde Facturas (asistente)
├── Seguimiento
│   ├── Letras en Cartera             (borrador/enviada/firmada)
│   ├── Proyección Semanal            (pivot / gráfico)
│   ├── Protestos                     (registro de protestos)
│   ├── Letras Protestadas            (listado filtrado)
│   └── Renovaciones                  (historial de renovaciones)
├── Reportes
│   ├── Proyección Semanal (Pivot)
│   ├── Estado de Cuenta              (elige cliente → Imprimir Estado de Cuenta)
│   └── Exportar Resumen Excel / Email
└── Configuración
    ├── Grupos Empresariales
    ├── Bancos
    └── Secuencias
```

**Acceso alternativo desde Contabilidad:** `Contabilidad → Clientes → Letras de Cambio`.

### 2.1 Descripción de cada Opción del Menú

| Opción de menú | Ruta | Para qué sirve |
|---|---|---|
| **Letras de Cambio** | Operaciones | Listado maestro de todas las letras. Permite crear, ver y filtrar; con vistas Lista, Kanban, Calendario, Pivot y Gráfico. |
| **Operaciones Cabal** | Operaciones | Mismo listado filtrado por **Tipo de Instrumento = Cabal** (sirve como *reporte de Cabal*). |
| **Planillas** | Operaciones | Crear y gestionar las planillas de envío al banco. |
| **Generar Letras desde Facturas** | Operaciones | Abrir el asistente para convertir facturas en letras. |
| **Letras en Cartera** | Seguimiento | Letras en estado Borrador/Enviada/Firmada (aún **no** enviadas al banco). |
| **Proyección Semanal** | Seguimiento | Tabla dinámica de cobros por vendedor/cliente/semana. |
| **Protestos** | Seguimiento | Historial y registro de protestos; permite **Regularizar**. |
| **Letras Protestadas** | Seguimiento | Listado filtrado de letras con estado *Protestada*. |
| **Renovaciones** | Seguimiento | Historial de renovaciones (letra origen ↔ letra nueva). |
| **Proyección Semanal (Pivot)** | Reportes | Acceso directo al Pivot/Gráfico de proyección. |
| **Estado de Cuenta** | Reportes | Abre la lista de clientes para imprimir su **Estado de Cuenta de Letras**. |
| **Exportar Resumen Excel / Email** | Reportes | Wizard para enviar por correo el resumen y/o generar el Excel. |
| **Grupos Empresariales** | Configuración | Administrar grupos y sus líneas de crédito. |
| **Bancos** | Configuración | Catálogo de bancos (BCP, Scotiabank, BBVA, etc.). |
| **Secuencias** | Configuración | Ver/editar las numeraciones de letra, planilla, protesto y renovación. |

---

## 3. CONFIGURACIÓN INICIAL Y DATOS MAESTROS

Antes de emitir letras conviene configurar el plazo de crédito por cliente y, si aplica, los Grupos Empresariales.

### 3.1 Ficha del Cliente (`res.partner`)

#### ¿Para qué sirve?
Asignar el plazo de crédito del cliente, vincularlo a un grupo empresarial y consultar su estado de bloqueo, su uso de crédito y sus letras.

#### Campo por campo (pestaña **Letras de Cambio**)

> *La pestaña solo se muestra para contactos de tipo **Compañía** (`is_company`).*

| Campo | Técnico | Descripción |
|---|---|---|
| **Grupo Empresarial** | `credit_group_id` | Grupo corporativo al que pertenece el cliente. Si tiene grupo, su crédito se calcula de forma **acumulada** entre todas las empresas. |
| **Plazo de Crédito (Letras)** | `letra_days_term` | Plazo por defecto para calcular el vencimiento: `30`, `60`, `90`, `120` o `150 Días (Anticipo)`. Al crear una letra, este plazo se propone automáticamente. |
| **Bloqueado Comercialmente** | `commercial_blocked` | Solo lectura. Se activa si el cliente (o su grupo) tiene letras protestadas pendientes de regularizar. Bloquea ventas, facturas y despacho. |
| **Motivo de Bloqueo** | `commercial_block_reason` | Texto que explica por qué el cliente está bloqueado. |
| **Cant. Letras** | `letra_count` | Número de letras activas del cliente (excluye canceladas y pagadas). |
| **Tiene Letras Protestadas** | `has_letras_protestadas` | Se marca si el cliente tiene al menos un protesto pendiente. |
| **% Uso Crédito** | `credit_usage_pct` | Porcentaje consumido de la línea de crédito de su grupo (`Crédito Utilizado / Línea`). |

> ⚠️ **Alerta de crédito:** cuando el **% Uso Crédito** llega a **90% o más**, aparece un **aviso amarillo** en esta pestaña (y también en el Pedido de Venta). Ver [sección 14](#14-alertas-y-automatizaciones).

Debajo se lista el detalle de **Letras** del cliente (N° Letra, Importe Total, Saldo, Vencimiento y Estado).

#### 🖱️ Guía paso a paso
1. Ve a **Ventas** o **Contabilidad → Clientes**.
2. Abre la ficha del cliente.
3. Entra a la pestaña **Letras de Cambio**.
4. Revisa/edita **Plazo de Crédito (Letras)** (ej. `60 Días`).
5. Si pertenece a un grupo, selecciona el **Grupo Empresarial**.
6. Revisa el **% Uso Crédito** y el aviso de crédito.
7. Guarda (`Ctrl + S`).

---

### 3.2 Grupos Empresariales (`l10n.pe.credit.group`)

#### ¿Para qué sirve?
Agrupa varias razones sociales que **comparten una misma línea de crédito** (ej. *Distribuidora KMT + Grupo Espinal*). La línea se controla de forma **agregada** para todo el grupo.

#### Campo por campo

| Campo | Técnico | Descripción |
|---|---|---|
| **Nombre del Grupo** | `name` | Nombre identificador (obligatorio). |
| **Empresas del Grupo** | `partner_ids` | Empresas que comparten la línea. |
| **Cant. Empresas** | `partner_count` | Número de empresas del grupo. |
| **Línea de Crédito Asignada** | `credit_limit` | Monto máximo en soles otorgado al grupo. |
| **Crédito Utilizado** | `credit_used` | Consumo total = facturas pendientes + pedidos por facturar + letras en circulación. |
| **Crédito Disponible** | `credit_available` | `Línea Asignada − Crédito Utilizado`. |
| **% de Uso** | `credit_usage_pct` | Porcentaje consumido de la línea (`Crédito Utilizado / Línea`). |
| **Pedidos Pendientes** | `pending_orders_amount` | Pedidos de venta confirmados pendientes de facturar. |
| **Facturado** | `invoiced_amount` | Facturas emitidas pendientes de pago. |
| **Aprobación de Excepción (Techo Global)** | `exception_approved` | Marcar cuando gerencia autorice **superar el techo agregado** de la compañía (RN-007). |
| **Aprobado por** | `exception_approved_by` | Usuario que autorizó la excepción (aparece al marcar la casilla). |

#### 🖱️ Guía paso a paso para crear un Grupo
1. Ve a **Letras de Cambio → Configuración → Grupos Empresariales**.
2. Clic en **Crear/Nuevo**.
3. Escribe el **Nombre del Grupo** (ej. `Grupo Comercial Espinal`).
4. Ingresa la **Línea de Crédito Asignada** (ej. `150000.00`).
5. En **Empresas del Grupo**, **Agregar una línea** y selecciona las empresas.
6. Guarda.

#### ⚠️ Regla del Techo Agregado (RN-007) — paso a paso
El **Techo Agregado** es el monto máximo que puede sumar **todas las líneas de crédito** de la compañía (se define en **Ajustes**, ver 3.3).
1. Si al guardar un grupo la suma de líneas **supera** el techo, Odoo **bloquea el guardado** con un mensaje.
2. Si gerencia autoriza la excepción, marca **Aprobación de Excepción (Techo Global)** y vuelve a guardar.
3. Indica en **Aprobado por** quién autorizó.
4. Guarda. El sistema permitirá el grupo pese a superar el techo.

---

### 3.3 Parámetros Globales (Ajustes)

#### ¿Para qué sirve?
Define el correo destino por defecto del envío de letras y el **Techo Agregado** de crédito de la compañía.

#### Campo por campo

| Campo | Técnico | Descripción |
|---|---|---|
| **Email para envío de Letras** | `letras_email_to` | Correo destino predeterminado (parámetro `l10n_pe_letras.email_to`). |
| **Techo Agregado de Líneas de Crédito** | `letras_global_credit_limit` | Monto máximo que puede sumar el total de líneas de crédito de **todos** los grupos. `0` = sin límite (RN-007). |

#### 🖱️ Guía paso a paso
1. Ve a **Ajustes**.
2. Baja hasta la sección **Letras de Cambio** (visible para Administradores de Contabilidad).
3. En **Email para envío**, escribe el correo (ej. `cobranzas@curpisco.com`).
4. En **Techo agregado de líneas de crédito**, ingresa el monto máximo (ej. `11360000.00`) o `0` para no aplicar límite.
5. Guarda.

---

## 4. EMISIÓN DE LETRAS DE CAMBIO

Hay dos vías: **automática desde facturas** (recomendada) o **manual**.

### 4.1 Generación Automática desde Facturas

#### 🖱️ Cómo abrir el asistente (3 rutas)
- **Desde Letras:** `Letras de Cambio → Operaciones → Generar Letras desde Facturas`.
- **Desde el listado de Letras:** botón **`Generar Letras desde Facturas`** en la barra superior.
- **Desde Facturación:** selecciona facturas en la lista → menú **Acciones** → **Generar Letras desde Facturas**.

#### Campo por campo del asistente

| Campo | Técnico | Descripción |
|---|---|---|
| **Opción de Generación** | `generate_option` | Ver las 3 opciones abajo. |
| **Facturas** | `invoice_ids` | Facturas a convertir. Se **auto-llenan** si venías de facturación. Solo admite facturas de cliente, **publicadas**, **no pagadas** y **no cubiertas aún por letras**. |
| **Cantidad de Letras (Cuotas)** | `num_letras` | Solo si eliges *Dividir en Cuotas*. Número de letras a generar. |
| **Intervalo (Días)** | `days_interval` | Solo si eliges *Dividir en Cuotas*. Días entre un vencimiento y el siguiente. |
| **Cliente** | `partner_id` | Solo lectura; se detecta de las facturas. |
| **Banco** | `bank_id` | Opcional; banco al que se destinarán. |
| **Fecha de Emisión** | `date_emission` | Por defecto hoy. |
| **Fecha Vencimiento (1ra Cuota / General)** | `date_due` | Fecha base. Si se deja vacía, se calcula con el plazo del cliente. |
| **Importe Total** | `amount_total` | Suma del **saldo disponible por letrear** de las facturas. |
| **Cronograma de Letras a Generar** | `line_ids` | Vista previa editable (cuota, concepto, vencimiento, monto). |

#### Las 3 opciones de generación
1. **Una Letra por Factura** → 1 letra por cada factura seleccionada.
2. **Una Letra por todas las Facturas** → consolida todas en 1 sola letra (mismo cliente).
3. **Dividir una Factura en Varias Letras (Cuotas)** → divide 1 factura en **N cuotas** con vencimientos escalonados (ej. 30/60/90 días) y ajuste de céntimos en la última.

#### 🖱️ Paso a paso
1. Abre el asistente (cualquiera de las 3 rutas).
2. Selecciona la **Opción de Generación**.
3. Revisa las **Facturas** (y cuotas/intervalo si divides).
4. Ajusta **Fecha de Emisión**, **Vencimiento** y **Banco** si hace falta.
5. En el **Cronograma**, edita fechas o montos de alguna cuota si el cliente lo pide.
6. Clic en **Generar Letra(s)**. Odoo crea las letras y te muestra el resultado.

---

### 4.2 Registro Manual (Formulario Campo por Campo)

Para una letra individual: `Letras de Cambio → Operaciones → Letras de Cambio → Nuevo`.

#### Datos Principales
| Campo | Técnico | Descripción |
|---|---|---|
| **N° Letra** | `name` | Correlativo automático (secuencia `LC-AAAA-00000`), único por compañía. |
| **Cliente** | `partner_id` | Razón social del deudor (obligatorio). Al elegirlo se autocompletan el vendedor y el plazo. |
| **Vendedor** | `salesperson_id` | Vendedor asignado al cliente (solo lectura, viene de la ficha del cliente). |
| **Tipo de Instrumento** | `instrument_type` | `Letra de Cambio` o `Cabal`. |
| **Tipo** | `tipo` | `Emisión` (letra original) o `Canje` (renovación/canje). |
| **Banco** | `bank_id` | Banco de descuento (BCP, Scotiabank, BBVA). |
| **Planilla** | `planilla_id` | Planilla en la que se incluyó la letra (solo lectura). |
| **Cargar Letra Firmada (PDF)** | `signed_document` | Archivo PDF de la letra firmada y sellada. **Solo PDF.** No se muestra en Cabal. |

#### Vencimiento y Banco
| Campo | Técnico | Descripción |
|---|---|---|
| **Fecha de Emisión** | `date_emission` | Fecha de expedición. |
| **Plazo en Días** | `days_term` | `30`, `60`, `90`, `120`, `150`. Se propone desde el cliente. |
| **Fecha de Vencimiento** | `date_due` | Emisión + plazo (editable). |
| **N° Único (Banco)** | `unique_number` | Número que asigna el banco; con él paga el cliente. |
| **Valor Banco (Interno)** | `internal_bank_number` | Número interno del banco para conciliación. |
| **Fecha de Pago** | `date_payment` | Fecha de cancelación (se llena al Registrar Pago). |
| **Fecha de Protesto** | `protest_date` | Aparece si la letra fue protestada. |
| **Nota de Débito (Gastos)** | `debit_note_id` | Nota de débito generada por el protesto. |
| **Moneda** | `currency_id` | Moneda de la compañía. |
| **Compañía** | `company_id` | Compañía (multi-compañía). |

#### Importes
| Campo | Técnico | Descripción |
|---|---|---|
| **Importe Total** | `amount_total` | **Se calcula automáticamente** sumando el **Monto Aplicado** de las facturas asociadas (también funciona por importación/API). |
| **Importe Pagado** | `amount_paid` | Total amortizado (al Registrar Pago se iguala al total). |
| **Saldo Pendiente** | `amount_residual` | `Importe Total − Importe Pagado`. |

#### Pestañas
- **Facturas Asociadas** (`line_ids`): facturas incluidas. Campos: **Factura** (`move_id`), **Monto Aplicado** (`amount`), **Saldo Factura** (`amount_residual`), **Fecha Factura** (`date_invoice`).
  - El selector de facturas filtra por el cliente, exige facturas **publicadas y no pagadas**, y **excluye las ya cubiertas** por letras (**RN-001**).
  - Al elegir una factura, el **Monto Aplicado** se autocompleta con el **saldo por letrear**.
- **Renovaciones**: letras destino (`renovacion_destino_ids`) y letra origen (`renovacion_origin_id`).
- **Observaciones** (`notes`): notas internas.
- **Chatter** (lateral): historial y adjuntos.

---

### 4.3 Reglas de Selección de Facturas

Para evitar el **doble conteo**, el sistema controla el estado de cada factura respecto a las letras:

| Estado Letras (`letra_state`) | Significado | ¿Se puede elegir? |
|---|---|---|
| `Sin Letra` | La factura no tiene letras | ✅ Sí |
| `Parcialmente en Letras` | Tiene letras pero **queda saldo por letrear** | ✅ Sí (solo el saldo pendiente) |
| `Totalmente en Letras` | Ya está cubierta por letras | ❌ No aparece en el selector |

- El **monto propuesto** al crear la letra es el **saldo disponible por letrear** (`Saldo Factura − Monto en Letras`).
- Si **cancelas** una letra, sus montos dejan de contar y la factura **vuelve a quedar disponible**.
- El sistema **impide por validación** que la suma de montos en letras de una factura supere su total.
- Solo se admiten facturas del **mismo cliente** (**RN-001**); intentar mezclar clientes produce un error.

---

## 5. CICLO DE VIDA DE LA LETRA (PASO A PASO)

### Vistas disponibles
En **Operaciones → Letras de Cambio** puedes alternar entre:
1. **Lista** (icono ☰): vista tabular con sumas.
2. **Kanban** (icono ▦): tarjetas agrupadas por **estado**, ideal para la ronda semanal.
3. **Calendario** (icono 📅): **vencimientos** del mes.
4. **Pivot** y **Gráfico**: análisis por vendedor/cliente/vencimiento.

> 🖱️ Cambia de vista con los **iconos de la esquina superior derecha** del listado.

### Estados
`Borrador` → `Enviada` → `Firmada` → `En Banco` → `Pagada` (o `Protestada`). También `Cancelada` y `Renovada`.

### Matriz de botones según estado

| Estado | Botones visibles |
|---|---|
| **Borrador** (`draft`) | Enviar al Cliente · Imprimir Letra para Firma · Anular |
| **Enviada** (`sent`) sin PDF | **Registrar Firma (gris, deshabilitado)** · Imprimir Letra para Firma · Anular |
| **Enviada** (`sent`) con PDF | **Registrar Firma (activo)** · Imprimir Letra para Firma · Anular |
| **Firmada** (`signed`) | Enviar al Banco · Registrar Pago · Ver Letra Firmada · Imprimir |
| **En Banco** (`in_bank`) | Registrar Pago · Registrar Protesto · Renovar · Ver Letra Firmada |
| **Protestada** (`protested`) | Renovar · Anular |
| **Cabal** | Enviar al Cliente y Enviar al Banco directo (no hay firma) |

### Paso 1 — Enviar al Cliente (`Borrador → Enviada`)
1. Abre la letra en **Borrador**.
2. Clic en **Enviar al Cliente**.
3. El estado pasa a **Enviada**. Usa **Imprimir Letra para Firma** para obtener el PDF y enviarlo al cliente.

### Paso 2 — Cargar la letra firmada y Registrar Firma (`Enviada → Firmada`)
1. Cuando el cliente devuelva la letra firmada y sellada, sube el **PDF** en el campo **Cargar Letra Firmada (PDF)**.
   - El sistema **solo acepta PDF**; otro formato es rechazado.
2. Sin archivo, el botón **Registrar Firma** se ve **gris (deshabilitado)**.
3. Al cargar el PDF, el botón se **activa en azul**.
4. Clic en **Registrar Firma**. El estado pasa a **Firmada**.

### Paso 3 — Enviar al Banco (`Firmada → En Banco`)
1. Clic en **Enviar al Banco**. (Valida que exista el PDF firmado.)
2. El estado pasa a **En Banco**. Asigna **N° Único** y **Valor Banco** cuando el banco los entregue.

### Paso 4 — Registrar Pago (`Firmada / En Banco → Pagada`)
1. Cuando el cliente cancela, clic en **Registrar Pago**.
2. El estado pasa a **Pagada**, se llena la **Fecha de Pago** y el **Saldo** queda en `0.00`.

### Consultar el PDF firmado
- Clic en **Ver Letra Firmada** para abrir/descargar el documento subido.

### Anular
- **Anular** pasa la letra a **Cancelada** (disponible desde Borrador/Enviada/Firmada).

---

## 6. MODALIDAD CABAL

### ¿Qué es?
Modalidad para clientes especiales en la que la factura se **canjea al 100% en el banco** (telecrédito) **sin letra ni firma física**. El cliente solo confirma el vencimiento por correo.

### ¿Dónde se elige?
No está en Ajustes: se elige por operación con el campo **Tipo de Instrumento**.

### 🖱️ Paso a paso
1. Ve a **Letras de Cambio → Operaciones → Operaciones Cabal** (o crea una letra y cambia **Tipo de Instrumento** a `Cabal`).
2. **Crear**.
3. Selecciona el **Cliente**.
4. El **Tipo de Instrumento** viene en `Cabal`.
5. En **Facturas Asociadas**, agrega la factura confirmada.
6. Guarda.
7. En Cabal **no se muestran** el campo de firma ni el botón **Registrar Firma**; se envía con **Enviar al Banco** directamente.

> 💡 El menú **Operaciones Cabal** funciona como **reporte de Cabal** (lista filtrada).

---

## 7. PLANILLAS DE ENVÍO AL BANCO

### ¿Para qué sirve?
Agrupar letras para presentarlas al banco (BCP, Scotiabank, BBVA).

### Campo por campo (`l10n.pe.letra.planilla`)

| Campo | Técnico | Descripción |
|---|---|---|
| **N° Planilla** | `name` | Correlativo (`PL-AAAA-00000`). |
| **Banco** | `bank_id` | Entidad receptora (obligatorio). |
| **Fecha** | `date` | Fecha de armado. |
| **Estado** | `state` | `Borrador` → `Enviada al Banco` → `Confirmada`. |
| **Importe Total** | `amount_total` | Suma de las letras incluidas. |
| **Cant. Letras** | `letra_count` | Número de letras incluidas. |
| **Letras** | `letra_ids` | Detalle de las letras (no canceladas). |
| **Observaciones** | `notes` | Notas. |

### 🖱️ Paso a paso
1. Ve a **Letras de Cambio → Operaciones → Planillas**.
2. **Crear**, selecciona el **Banco** y la **Fecha**.
3. En **Letras**, **Agregar una línea** y elige las letras a incluir.
4. Guarda.
5. **Enviar al Banco** para marcar la planilla como *Enviada al Banco* (luego **Confirmar** cuando el banco la acepte).
6. Imprime:
   - **Imprimir Planilla:** PDF resumen de la planilla (firma de Gerencia / recepción del banco).
   - **Imprimir Letras:** un solo PDF con todas las letras incluidas.

> ℹ️ El botón **Enviar al Banco** de la *planilla* solo cambia el estado de la planilla. Cada letra se envía al banco desde su propio botón **Enviar al Banco** (donde queda en estado *En Banco* y se asocia a la planilla).

---

## 8. PROTESTO DE LETRAS

### ¿Cuándo ocurre?
Cuando el cliente no paga al vencimiento (más los 8 días de gracia del banco), el banco debita el importe a Curpisco y la letra **protesta**.

### 🖱️ Registrar un protesto
1. Abre la letra en estado **En Banco**.
2. Clic en **Registrar Protesto**.
3. Completa:
   - **Fecha de Protesto** (`date_protest`).
   - **Monto Protestado** (`amount`).
   - **Gastos y Costas** (`gastos`).
   - **Total** (`total`): suma automática.
   - **Observaciones** (`notes`).
4. Guarda.

### ⚡ Efectos automáticos
1. La letra pasa a **Protestada** y guarda su **Fecha de Protesto**.
2. Se genera un **borrador de Nota de Débito** (`account.move`) al cliente por los **Gastos y Costas**, vinculado en la letra (`debit_note_id`). *(Si los gastos son 0, no se genera nota.)*
3. El cliente y su **Grupo Empresarial** quedan **bloqueados comercialmente** (no se les puede vender ni validar facturas).

### 🖱️ Regularizar
1. Ve a **Letras de Cambio → Seguimiento → Protestos**.
2. Abre el protesto en estado **Pendiente**.
3. Clic en **Regularizar** y registra **Fecha de Regularización** y **Tipo** (`Pago`, `Renovación`, `Acuerdo`, `Otro`).
4. Al no quedar protestos pendientes, el **bloqueo comercial se levanta**.

### Campo por campo (`l10n.pe.letra.protesto`)

| Campo | Técnico | Descripción |
|---|---|---|
| **N° Protesto** | `name` | Correlativo (`PR-AAAA-00000`). |
| **Letra** | `letra_id` | Letra protestada. |
| **Cliente** | `partner_id` | Cliente (autocompletado). |
| **Fecha de Protesto** | `date_protest` | Fecha del protesto. |
| **Monto Protestado** | `amount` | Importe no pagado. |
| **Gastos y Costas** | `gastos` | Gastos bancarios/notariales. |
| **Total** | `total` | Suma automática. |
| **Estado** | `state` | `Pendiente` / `Regularizado`. |
| **Fecha de Regularización** | `resolution_date` | Fecha de solución. |
| **Tipo de Regularización** | `resolution_type` | Forma de solución. |
| **Nota de Débito (Gastos)** | `debit_note_id` | Documento generado. |
| **Observaciones** | `notes` | Notas. |

---

## 9. RENOVACIÓN DE LETRAS

### ¿Cuándo se aplica?
Cuando el cliente paga solo una parte y se difiere el saldo en una **nueva letra**. El plazo de renovación es **siempre 30 días** (impuesto por el banco).

### 🖱️ Paso a paso
1. Abre la letra en estado **En Banco** o **Protestada**.
2. Clic en **Renovar**.
3. En el asistente **Renovar Letra**, completa:

| Campo | Técnico | Descripción |
|---|---|---|
| **Letra a Renovar** | `letra_origin_id` | Letra origen (solo lectura). |
| **Cliente** | `partner_id` | Cliente (solo lectura). |
| **Banco** | `bank_id` | Banco. |
| **Fecha de Emisión** | `date_emission` | Fecha de la nueva letra. |
| **Plazo Renovación** | `days_term` | Fijado en `30 Días (Obligatorio Banco)` (no editable). |
| **Nueva Fecha de Vencimiento** | `date_due` | Calculada a 30 días. |
| **Monto Original** | `amount_origin` | Saldo de la letra origen. |
| **Intereses** | `intereses` | Intereses de la prórroga. |
| **Gastos** | `gastos` | Gastos administrativos. |
| **Nuevo Monto** | `amount_new` | Se calcula como `Monto Original + Intereses + Gastos`. |
| **Motivo de Renovación** | `reason` | Texto del acuerdo. |

4. Clic en **Generar Renovación**.

### ⚡ Efectos
1. La letra original pasa a **Renovada**.
2. Se crea una **nueva letra** (tipo *Canje*) a 30 días con el nuevo monto.
3. Queda el vínculo de trazabilidad (origen/destino) y un registro en **Renovaciones**.

---

## 10. PROYECCIÓN SEMANAL DE COBRANZA

Reemplaza el Excel manual de la reunión de los lunes.

### 🖱️ Cómo consultarla
1. Ve a **Letras de Cambio → Seguimiento → Proyección Semanal** (o **Reportes → Proyección Semanal (Pivot)**).
2. Se abre una **Tabla Dinámica (Pivot)**:
   - **Filas:** Vendedor (`salesperson_id`) → Cliente (`partner_id`).
   - **Columnas:** Vencimiento (`date_due`).
   - **Medidas:** Importe Total y Saldo Pendiente.
3. Para ver el **Gráfico de Barras**, cambia al ícono de gráficos (arriba a la derecha).
4. Filtra por Banco, Estado o Vendedor desde la barra de búsqueda (agrupador **Vencimiento**).

---

## 11. ENVÍO POR EMAIL Y EXPORTACIÓN EXCEL

### 🖱️ Paso a paso
1. Ve a **Letras de Cambio → Reportes → Exportar Resumen Excel / Email**.
2. En el wizard **Enviar Letras por Email**:

| Campo | Técnico | Descripción |
|---|---|---|
| **Desde / Hasta** | `date_from` / `date_to` | Rango de fechas de emisión. |
| **Filtrar por Estado** | `state` | Estado a incluir (`En Banco`, `Protestada`, etc.). |
| **Enviar a** | `email_to` | Correo destino (autocompletado desde Ajustes). |
| **Incluir PDF por letra** | `include_report` | Adjunta el PDF individual de cada letra. |
| **Incluir Excel resumen** | `include_excel` | Genera la hoja de cálculo `.xlsx`. |
| **Letras a enviar** | `letra_count` | Solo lectura; cuántas letras coinciden. |

3. Usa **Vista Previa** para revisar, o **Enviar Letras** para despachar.
4. El sistema **envía un correo real** (con PDFs y/o Excel adjuntos) y deja constancia en el **Chatter**.

> ⚠️ Requisito: debe estar configurado el **servidor de correo saliente** en Odoo (`Ajustes → Correo saliente`). El Excel se genera con `openpyxl`.

---

## 12. REGLAS DE NEGOCIO Y BLOQUEOS

### Reglas aplicadas
| Regla | Descripción |
|---|---|
| **RN-001 · Facturas del mismo cliente** | Solo se pueden asociar facturas de cliente **publicadas**, **no pagadas** y del **mismo cliente**. |
| **RN-002 · Vencimiento** | El vencimiento = **Fecha de Emisión + Plazo** del cliente (campo calculado). |
| **RN-003 · Firma obligatoria** | No se registra la firma ni se envía al banco una *Letra de Cambio* sin el **PDF firmado** cargado. |
| **RN-004 · Plazo de renovación** | Toda renovación se genera a **30 días**. |
| **RN-005 · Nota de débito** | Al protestar con gastos, se genera la nota de débito al cliente. |
| **RN-006 · Bloqueo por protesto** | Cliente con letra protestada no puede comprar (**venta**) ni **validar facturas**, hasta regularizar. |
| **RN-007 · Techo agregado** | La suma de líneas de crédito de los grupos no puede superar el **Techo Agregado** de la compañía, salvo **Aprobación de Excepción**. |
| **RN-008 · Grupo comparte línea** | Las empresas de un grupo comparten una única línea de crédito (control agregado). |
| **RN-009 · Cabal sin firma** | El instrumento `Cabal` no exige documento firmado. |
| **Anti doble conteo** | No se pueden elegir facturas ya cubiertas por letras; la suma de montos en letras no puede superar el total de la factura. |
| **Canceladas** | Las letras canceladas dejan de contar; la factura vuelve a quedar disponible. |
| **Importe automático** | El importe de la letra se calcula desde las facturas asociadas (campo calculado, válido también por importación/API). |

### Bloqueo comercial
- **Pedidos de Venta (`sale.order`):** si el cliente está bloqueado, Odoo **impide confirmar** el pedido. Si pertenece a un Grupo y el **crédito disponible** es menor al total del pedido, también se **impide confirmar**.
- **Facturas (`account.move`):** no se puede **validar** una factura de cliente si el cliente está bloqueado (la **nota de débito de protesto** sí se permite).
- **Alerta preventiva:** cuando el cliente usa **≥ 90%** de la línea de su grupo, aparece un **aviso amarillo** en la ficha del cliente y en el Pedido de Venta.

---

## 13. CATÁLOGO DE REPORTES

| # | Reporte | Tipo | Acceso |
|---|---|---|---|
| 1 | **Letra de Cambio** (`action_report_letra`) | PDF | Letra → **Imprimir Letra para Firma** o menú **Imprimir** |
| 2 | **Letra Firmada** | Archivo PDF | Letra → **Ver Letra Firmada** (abre/descarga el PDF subido) |
| 3 | **Planilla de Letras** (`action_report_letra_planilla`) | PDF | Planilla → **Imprimir Planilla** / **Imprimir Letras** |
| 4 | **Estado de Cuenta de Letras** (`action_report_estado_cuenta_partner`) | PDF | Cliente → **Imprimir → Estado de Cuenta de Letras** |
| 5 | **Proyección Semanal** (`action_proyeccion_cobranza`) | Pivot / Gráfico | `Reportes → Proyección Semanal (Pivot)` |
| 6 | **Resumen Ejecutivo de Cartera** | Excel `.xlsx` | `Reportes → Exportar Resumen Excel / Email` |
| 7 | **Letras en Cartera** (`action_letra_cartera`) | Lista / Kanban / Calendario | `Seguimiento → Letras en Cartera` |
| 8 | **Letras Protestadas** (`action_letra_protestadas`) | Lista | `Seguimiento → Letras Protestadas` |
| 9 | **Cabal** (`action_letra_cabal`) | Lista / Kanban | `Operaciones → Operaciones Cabal` |

### Detalle
1. **Letra de Cambio (PDF).** Formato oficial: girador (Curpisco), aceptante, importe en soles, fechas, banco, tabla de facturas y recuadros de **Firma del Girador** y **Aceptación**. Sirve para imprimir y enviar al cliente **a firmar**.
2. **Letra Firmada.** No es un reporte QWeb: **abre/descarga** el PDF que cargaste como sustento (para enviar al banco).
3. **Planilla de Letras (PDF).** Relación de letras con total, cantidad y firmas de **Entregado por** (Gerencia) y **Recibido por** (banco). **Imprimir Letras** descarga todas las letras en un solo PDF.
4. **Estado de Cuenta de Letras (PDF).** Muestra **línea de crédito vs. utilizado vs. disponible**, estado de bloqueo y detalle de letras activas.
5. **Proyección Semanal (Pivot/Gráfico).** Vencimientos por vendedor/cliente/semana.
6. **Resumen Ejecutivo (Excel).** Hoja con formato corporativo, moneda `#,##0.00`, totales y metadatos.

---

## 14. ALERTAS Y AUTOMATIZACIONES

### 14.1 Alerta preventiva de crédito (≥ 90%)
#### ¿Para qué sirve?
Avisar **antes** de que un cliente agote su línea de crédito, para negociar (prepago, letras nuevas, etc.).

#### ¿Cómo funciona?
- El sistema calcula el **% Uso** = `Crédito Utilizado / Línea del Grupo`.
- Cuando llega a **90% o más**, aparece un **aviso amarillo**.

#### 🖱️ Dónde verla
- **Ficha del cliente** → pestaña **Letras de Cambio** (campo **% Uso Crédito**).
- **Pedido de Venta** → pestaña **Letras de Cambio**.
- **Grupo Empresarial** → campo **% de Uso**.

> 💡 La alerta es **informativa**: no bloquea por sí sola. El bloqueo ocurre solo si el pedido supera el **crédito disponible** o si el cliente está **protestado**.

### 14.2 Recordatorio de vencimiento (día 6/7/8)
#### ¿Para qué sirve?
Reemplazar el aviso manual por WhatsApp: el sistema genera **actividades** de seguimiento para las letras próximas a vencer.

#### ¿Cómo funciona?
- Una acción programada diaria (**Letras: recordatorio de vencimiento**) revisa las letras en estado **En Banco** que vencen en los **próximos 7 días**.
- Por cada una, crea una **actividad** asignada al usuario, con el resumen *"Letra X próxima a vencer"*.
- **No** duplica la actividad si ya existe.

#### 🖱️ Cómo ver las actividades
1. En la barra superior de Odoo, haz clic en el ícono de **Actividades** ⏰.
2. Verás las letras a contactar con su fecha límite.

#### 🖱️ Cómo ejecutarlo manualmente (para probar)
1. Ve a **Ajustes → Técnico → Acciones Programadas** (requiere modo desarrollador).
2. Busca **"Letras: recordatorio de vencimiento"**.
3. Clic en **Ejecutar manualmente** (Run Manually).
4. Revisa el ícono de **Actividades** o el **Chatter** de la letra.

---

## 15. SEGURIDAD Y ROLES

### Grupos del módulo
| Grupo | Quién | Permisos |
|---|---|---|
| **Letras de Cambio / Usuario** (`group_letra_user`) | Operadora de Créditos y Cobranzas (Katy) | Ver, crear y editar letras/planillas; **sin eliminar**. |
| **Letras de Cambio / Administrador** (`group_letra_manager`) | Responsable de sistemas / jefatura | Todos los permisos (incluida eliminación y configuración). |

Además, por permisos estándar, los **usuarios internos** pueden ver/crear/editar y los **Administradores de Contabilidad** tienen control total.

### 🖱️ Cómo asignar el grupo a un usuario
1. Ve a **Ajustes → Usuarios y Compañías → Usuarios**.
2. Abre el usuario (ej. Katy).
3. En **Derechos de acceso**, sección **Letras de Cambio**, marca **Usuario** o **Administrador**.
4. Guarda.

> ⚠️ El usuario **administrador/superusuario** de Odoo no requiere asignación.

### Multi-compañía
- Las **letras**, **planillas** y **grupos** que ve un usuario son solo de las **compañías** a las que tiene acceso. No se mezclan datos entre compañías.

---

## 16. APÉNDICE A — Novedades de esta Versión

Resumen de lo ajustado en la versión **`19.0.1.40.0`**:

| # | Novedad | Qué cambió |
|---|---|---|
| 1 | **RN-001** | Se valida que las facturas sean del **mismo cliente**, **publicadas** y **no pagadas**. |
| 2 | **RN-006 ampliado** | Además de Pedidos de Venta, ahora se **bloquea la validación de facturas** de clientes protestados (la nota de débito de protesto se permite). |
| 3 | **RN-007** | Nuevo **Techo Agregado** de líneas de crédito por compañía + **Aprobación de Excepción** por grupo. |
| 4 | **Importe automático** | El **Importe Total** de la letra se calcula desde las facturas (válido por importación/API). |
| 5 | **Vistas** | Se agregaron **Kanban** y **Calendario**. |
| 6 | **Menús** | Nuevos accesos: **Letras en Cartera**, **Letras Protestadas**, **Estado de Cuenta**, **Bancos** y **Secuencias**. |
| 7 | **Recordatorio de vencimiento** | Acción programada diaria que crea **actividades** (día 6/7/8). |
| 8 | **Alerta de crédito ≥ 90%** | Aviso amarillo en cliente y pedido de venta; campo **% Uso Crédito**. |
| 9 | **Seguridad** | Los grupos **Letras/Usuario** y **Letras/Administrador** ahora están activos. |
| 10 | **Pruebas automáticas** | Se incorporaron pruebas base de reglas de negocio. |

---

## 17. APÉNDICE B — Checklist de Verificación

Usa esta lista para probar el módulo paso a paso (tras **Actualizar** el módulo):

| ✔ | Prueba | Cómo verificarlo |
|---|---|---|
| ☐ | **RN-001** | Crea una letra y agrega una factura de **otro** cliente → debe dar error. |
| ☐ | **Selección de facturas** | Una factura ya cubierta por letras **no aparece** en el selector. |
| ☐ | **Importe automático** | Cambia el **Monto Aplicado** de una línea → el **Importe Total** se recalcula. |
| ☐ | **Firma solo PDF** | Sube un archivo que no sea PDF → debe rechazarlo. |
| ☐ | **Botón Registrar Firma** | Sin PDF se ve **gris**; al subir el PDF se **activa**. |
| ☐ | **Ver Letra Firmada** | Con PDF cargado, el botón abre/descarga el documento. |
| ☐ | **RN-003** | Intenta **Enviar al Banco** sin PDF → debe bloquear. |
| ☐ | **Protesto + Nota de Débito** | Registra un protesto con gastos → se genera la **nota de débito** y se bloquea al cliente. |
| ☐ | **RN-006 en facturas** | Con el cliente bloqueado, intenta **validar** una factura → debe bloquear. |
| ☐ | **RN-004** | Renueva una letra → la nueva letra vence a **30 días**. |
| ☐ | **Registrar Pago** | Registra el pago → **Saldo = 0.00**. |
| ☐ | **RN-007** | Pon un techo bajo en Ajustes y guarda un grupo que lo exceda → error; marca **Excepción** → guarda. |
| ☐ | **Alerta ≥ 90%** | Con uso ≥ 90%, revisa cliente y pedido de venta → **aviso amarillo**. |
| ☐ | **Kanban / Calendario** | Cambia de vista en **Operaciones → Letras de Cambio**. |
| ☐ | **Menús nuevos** | Revisa Seguimiento (Cartera/Protestadas), Reportes (Estado de Cuenta) y Configuración (Bancos/Secuencias). |
| ☐ | **Recordatorio** | Ejecuta la acción programada → aparece una **actividad** en letras por vencer. |
| ☐ | **Grupos de seguridad** | Asigna **Letras/Usuario** a un usuario y prueba crear/editar (sin eliminar). |

---

*Fin del manual.*
