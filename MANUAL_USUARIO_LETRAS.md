# MANUAL DE USUARIO Y OPERATIVO
## MÓDULO DE LETRAS DE CAMBIO Y COBRANZAS PERÚ
### Curpisco · Odoo 19 Enterprise / Community

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción y Visión General](#1-introducción-y-visión-general)
2. [Configuración Inicial y Datos Maestros](#2-configuración-inicial-y-datos-maestros)
   - [2.1 Configuración de Clientes (res.partner)](#21-configuración-de-clientes-respartner)
   - [2.2 Configuración de Grupos Empresariales (l10n.pe.credit.group)](#22-configuración-de-grupos-empresariales-l10npecreditgroup)
   - [2.3 Configuración de Parámetros Globales](#23-configuración-de-parámetros-globales)
   - [2.4 Grupos de Seguridad del Módulo](#24-grupos-de-seguridad-del-módulo)
3. [Operación 1: Emisión y Generación de Letras de Cambio](#3-operación-1-emisión-y-generación-de-letras-de-cambio)
   - [3.1 Generación Automática desde Facturas de Cliente](#31-generación-automática-desde-facturas-de-cliente)
   - [3.2 Registro y Gestión de la Letra de Cambio Formulario a Detalle](#32-registro-y-gestión-de-la-letra-de-cambio-formulario-a-detalle)
   - [3.3 Ciclo de Vida y Transición de Estados (Clic a Clic)](#33-ciclo-de-vida-y-transición-de-estados-clic-a-clic)
4. [Operación 2: Modalidad "CABAL" (Canje 100% Factura)](#4-operación-2-modalidad-cabal-canje-100-factura)
5. [Operación 3: Agrupación y Envío de Planillas al Banco](#5-operación-3-agrupación-y-envío-de-planillas-al-banco)
6. [Seguimiento 1: Protesto de Letras de Cambio](#6-seguimiento-1-protesto-de-letras-de-cambio)
7. [Seguimiento 2: Renovación de Letras de Cambio](#7-seguimiento-2-renovación-de-letras-de-cambio)
8. [Seguimiento 3: Proyección Semanal de Cobranza (Pivot / Gráfico)](#8-seguimiento-3-proyección-semanal-de-cobranza-pivot--gráfico)
9. [Seguimiento 4: Envío Masivo por Email y Exportación Excel](#9-seguimiento-4-envío-masivo-por-email-y-exportación-excel)
10. [Matriz de Seguridad, Bloqueos Comerciales y Reglas de Negocio](#10-matriz-de-seguridad-bloqueos-comerciales-y-reglas-de-negocio)

---

## 1. INTRODUCCIÓN Y VISIÓN GENERAL

El módulo **`l10n_pe_letras`** ha sido diseñado a medida para gestionar el ciclo completo de cobranzas con **Letras de Cambio al Descuento Bancario** y operaciones **Cabal** en empresas peruanas bajo Odoo 19.

### Objetivos principales:
- **Automatización del Canje:** Convertir facturas de clientes en letras individuales o agrupadas.
- **Control de Riesgo Crediticio:** Evaluar líneas de crédito individuales y por Grupo Empresarial.
- **Bloqueo Comercial Automático:** Detener automáticamente la confirmación de Pedidos de Venta (`sale.order`) si un cliente excede su línea de crédito o posee letras protestadas sin regularizar.
- **Descuento Bancario:** Armar planillas físicas y electrónicas para envío a bancos (BCP, Scotiabank, BBVA).
- **Control de Protestos y Renovaciones:** Registrar protestos con generación automática de Nota de Débito por gastos bancarios y aplicar renovaciones con plazo fijo de 30 días.
- **Proyección Semanal Integrada:** Eliminar los reportes manuales en Excel mediante vistas Pivot dinámicas por vendedor y semana de vencimiento.

---

## 2. CONFIGURACIÓN INICIAL Y DATOS MAESTROS

Antes de iniciar la emisión de letras, deben configurarse los parámetros de crédito en la ficha del cliente y los Grupos Empresariales.

### 2.1 Configuración de Clientes (`res.partner`)

#### ¿Para qué sirve?
Permite asignar el plazo de crédito predeterminado para las letras de cada cliente, vincularlo a un grupo empresarial y consultar su estado de bloqueo y letras protestadas.

#### Explicación Campo por Campo:
- **Grupo Empresarial (`credit_group_id`):** Selecciona el grupo corporativo al que pertenece el cliente. Si pertenece a un grupo, la línea de crédito se calculará de forma acumulada entre todas las empresas del grupo.
- **Plazo de Crédito (Letras) (`letra_days_term`):** Define el plazo predeterminado en días para el cálculo automático de la fecha de vencimiento (`30 Días`, `60 Días`, `90 Días`, `120 Días`, `150 Días (Anticipo)`).
- **Cliente Cabal (`is_cabal_client`):** Marca este cliente como operación **Cabal** (canje de factura al 100% en el banco, sin letra ni firma física). Al generar una letra desde sus facturas o seleccionarlo en una letra, el sistema propondrá automáticamente el *Tipo de Instrumento* = `Cabal`.
- **Bloqueado Comercialmente (`commercial_blocked`):** Indicador tipo Checkbox (solo lectura / computado). Se marca automáticamente en **rojo/activo** si el cliente o su grupo empresarial tienen letras protestadas pendientes de regularizar. El valor se recalcula en tiempo real cada vez que se crea o regulariza un protesto.
- **Motivo de Bloqueo (`commercial_block_reason`):** Muestra el texto explicativo del motivo por el cual el cliente no puede recibir nuevos pedidos confirmados.
- **Cant. Letras (`letra_count`):** Contador inteligente que muestra el total de letras activas en circulación del cliente.
- **Tiene Letras Protestadas (`has_letras_protestadas`):** Marca `True` si el cliente tiene al menos un protesto pendiente de regularizar.

#### 🖱️ Guía Clic a Clic para configurar un cliente:
1. Ve al menú **Ventas** (o **Contabilidad**) -> **Clientes**.
2. Haz clic sobre el cliente que deseas configurar.
3. Haz clic en la pestaña **Letras de Cambio** (ubicada dentro del contenedor principal de pestañas).
4. Haz clic en el botón **Editar** (o modifica directamente los campos).
5. En **Plazo de Crédito (Letras)**, selecciona el plazo contractual (ejemplo: `60 Días`).
6. Si el cliente pertenece a un grupo corporativo, selecciona el **Grupo Empresarial** correspondiente.
7. Haz clic en el icono **Guardar manualmente** (o Ctrl+S).

---

### 2.2 Configuración de Grupos Empresariales (`l10n.pe.credit.group`)

#### ¿Para qué sirve?
Controla el techo agregado de crédito otorgado a un conjunto de razones sociales hermanas (por ejemplo: *Distribuidora KMT + Grupo Espinal*).

#### Explicación Campo por Campo:
- **Nombre del Grupo (`name`):** Nombre identificador del grupo empresarial (Obligatorio).
- **Empresas del Grupo (`partner_ids`):** Listado de empresas que comparten la misma línea de crédito.
- **Línea de Crédito Asignada (`credit_limit`):** Monto máximo total en soles (S/) otorgado al grupo corporativo.
- **Crédito Utilizado (`credit_used`):** Monto total consumido (Facturas no pagadas + Pedidos de venta por facturar + Letras en circulación).
- **Crédito Disponible (`credit_available`):** Resultado de `Línea Asignada - Crédito Utilizado`.
- **Pedidos Pendientes (`pending_orders_amount`):** Suma total de cotizaciones/pedidos de venta confirmados pendientes de facturación.
- **Facturado (`invoiced_amount`):** Suma total de facturas emitidas pendientes de pago.
- **Aprobación de Excepción (Techo Global) (`exception_approved`):** Casilla que debe marcar gerencia cuando la suma de líneas del grupo supera el **Techo Agregado** configurado en la compañía; sin esta marca el sistema bloquea el guardado del grupo.
- **Aprobado por (`exception_approved_by`):** Usuario que autorizó la excepción al techo global.

#### 🖱️ Guía Clic a Clic para crear un Grupo Empresarial:
1. Ve al menú principal **Letras de Cambio** -> **Configuración** -> **Grupos Empresariales**.
2. Haz clic en el botón **Crear** (o **Nuevo**).
3. Ingresa el **Nombre del Grupo** (ejemplo: `Grupo Comercial Espinal`).
4. Ingresa la **Línea de Crédito Asignada** (ejemplo: `150000.00`).
5. En la tabla **Empresas del Grupo**, haz clic en **Agregar una línea** y selecciona las empresas pertenecientes.
6. Haz clic en **Guardar**.
   > *Si el sistema muestra un error indicando que se supera el **Techo Agregado** de la compañía, solicita autorización de gerencia y marca la casilla **Aprobación de Excepción (Techo Global)** para poder guardar (ver Regla RN-007).*

---

### 2.3 Configuración de Parámetros Globales

#### ¿Para qué sirve?
Define el correo electrónico corporativo al cual se enviará por defecto el resumen masivo de letras y reportes en Excel, y el techo agregado de líneas de crédito de la compañía.

#### Explicación Campo por Campo:
- **Email para envío de Letras:** Correo destino predeterminado para el wizard *Enviar Letras por Email*.
- **Techo Agregado de Líneas de Crédito (`letras_global_credit_limit`):** Monto máximo (S/) que puede sumar el total de líneas de crédito otorgadas a **todos** los grupos empresariales de la compañía. Si un grupo se guarda superando este techo (y no tiene marcada la *Aprobación de Excepción*), el sistema lo impide (Regla RN-007). Use `0` para no aplicar límite.

#### 🖱️ Guía Clic a Clic:
1. Ve a **Ajustes** -> desplázate a la sección **Letras de Cambio**.
2. En el campo **Email para envío de Letras**, ingresa la dirección de correo (ejemplo: `cobranzas@curpisco.com`).
3. En el campo **Techo agregado de líneas de crédito**, ingresa el monto máximo (ejemplo: `11360000.00`) o `0` para desactivarlo.
4. Haz clic en **Guardar**.

---

### 2.4 Grupos de Seguridad del Módulo

El módulo define dos grupos de seguridad propios. **Es obligatorio asignar** a los operadores de créditos y cobranzas, de lo contrario no podrán crear ni editar letras, planillas, protestos ni renovaciones.

| Grupo | A quién asignar | Permisos |
|---|---|---|
| **Letras de Cambio / Usuario** | Operadora de Créditos y Cobranzas (Katy) | Crear, leer y modificar letras, planillas, protestos y renovaciones. Sin eliminar. |
| **Letras de Cambio / Administrador** | Responsable de sistemas / jefatura | Todos los permisos, incluida la eliminación y la configuración. |

#### 🖱️ Guía Clic a Clic para asignar el grupo:
1. Ve a **Ajustes** -> **Usuarios y Compañías** -> **Usuarios**.
2. Abre el usuario (por ejemplo, Katy).
3. En la pestaña **Derechos de acceso**, en la sección **Letras de Cambio**, selecciona **Usuario** o **Administrador** según corresponda.
4. Haz clic en **Guardar**.
   > *Nota:* El usuario administrador/superusuario de Odoo no requiere asignación, ya que omite todas las reglas de acceso.

---

## 3. OPERACIÓN 1: EMISIÓN Y GENERACIÓN DE LETRAS DE CAMBIO

Existen dos maneras de emitir una letra: automáticamente desde facturas publicadas o manualmente.

### 3.1 Generación Automática desde Facturas de Cliente y Asistente de Cuotas

#### 🖱️ Guía Clic a Clic:
1. **Acceso desde el módulo de Letras de Cambio:**
   - Ve al menú **Letras de Cambio** -> **Operaciones** -> **Letras de Cambio**.
   - En el encabezado superior verás dos botones principales:
     - **`[ Nueva Letra ]`**: Para registrar manualmente una letra de cambio individual de forma limpia.
     - **`[ Más opciones de letras ]`**: Para abrir el asistente interactivo de cuotas y generación masiva.
   - *Rutas alternativas para abrir el asistente:*
     - Desde el menú: **Letras de Cambio** -> **Operaciones** -> **Generar Letras desde Facturas**.
     - Desde Facturación: Selecciona facturas en el listado de **Facturas** -> menú de **Acciones** -> **Generar Letras desde Facturas**.

2. **Ventana Emergente del Asistente (*Wizard*) con Pre-llenado Automático:**
   - **Facturas seleccionadas:** Se auto-seleccionan automáticamente las facturas elegidas.
   - **Cliente:** Se autocompleta el cliente asociado.
   - **Fecha de Emisión:** Muestra por defecto la fecha del día.
   - **Fecha Vencimiento (1ra Cuota / General):** Campo editable para definir la fecha inicial o base.
   - **Banco:** (Opcional) Selecciona el banco emisor.
   - **Opción de Generación:**
     - `Una Letra por Factura`: Crea 1 letra individual por cada factura seleccionada.
     - `Una Letra por todas las Facturas`: Consolida el saldo total de las facturas en una sola letra.
     - `Dividir una Factura en Varias Letras (Cuotas)`: Permite fraccionar 1 factura en **N cuotas** (ej. 3 letras) definiendo el intervalo en días entre cuotas (ej. cada 30 días).

3. **Vista Previa Interactiva del Cronograma:**
   - Abajo en el asistente verás la tabla **Cronograma de Letras a Generar (Vista Previa)** que muestra en tiempo real:
     - N° de Cuota / Concepto.
     - Fecha de vencimiento exacta de cada cuota.
     - Monto exacto calculado de cada cuota con ajuste automático de céntimos en la última cuota.
   - *Tip UX:* Puedes editar directamente en la tabla las fechas de vencimiento o importes celda por celda si deseas personalizar una cuota específica antes de confirmar.

4. Haz clic en el botón **Generar Letra(s)**. El sistema creará las letras exactamente como figuran en la vista previa y te llevará al listado de letras generadas.


---

### 3.2 Registro y Gestión de la Letra de Cambio (Formulario a Detalle)

#### 🖱️ Registro Manual Ultrarrápido (`Nueva Letra`):
1. Haz clic en el botón **`Nueva Letra`** en el listado de Letras de Cambio.
2. Selecciona el **Cliente** (`partner_id`).
3. En la pestaña **Facturas Asociadas**, haz clic en **Agregar una línea**:
   - En el selector de **Factura**, el sistema **filtrará automáticamente mostrando sólo las facturas abiertas de ese cliente**.
   - Al seleccionar la factura, el **Monto Aplicado** se autocompletará automáticamente con el saldo pendiente de la factura.
   - El **Importe Total** de la letra se recalculará dinámicamente sumando las facturas asociadas.
4. Revisa o modifica la **Fecha de Vencimiento** (calculada según los días acordados con el cliente, pero 100% editable).
5. Haz clic en **Guardar**.

#### Explicación Campo por Campo de la Letra (`l10n.pe.letra`):

##### Encabezado y Datos Generales:
- **N° Letra (`name`):** Correlativo interno asignado automáticamente por el sistema (ejemplo: `LET/2026/00001`).
- **Cliente (`partner_id`):** Razón social del deudor (Obligatorio).
- **Vendedor (`salesperson_id`):** Vendedor asignado comercialmente al cliente (Autocompletado).
- **Tipo de Instrumento (`instrument_type`):**
  - `Letra de Cambio`: Requiere firma y sello físico del cliente antes de enviar al banco.
  - `Cabal`: Operación directa en telecrédito sin requerimiento de documento físico firmado.
- **Tipo (`tipo`):** `Emisión` (letra original de venta) o `Canje` (letra producto de renovación o canje especial).
- **Banco (`bank_id`):** Banco asignado para el descuento (BCP, Scotiabank, BBVA).
- **Planilla (`planilla_id`):** Planilla bancaria en la que fue enviada la letra (Autocompletado al asociar a planilla).
- **Cargar Letra Firmada (PDF) (`signed_document`):** Campo de carga de archivo donde se sube la letra firmada y sellada por el cliente. **Solo acepta archivos PDF.** Es obligatorio para poder registrar la firma y enviar al banco (excepto en instrumentos tipo `Cabal`, donde el campo no se muestra).

##### Fechas y Plazos:
- **Fecha de Emisión (`date_emission`):** Fecha de expedición del documento.
- **Plazo en Días (`days_term`):** Plazo otorgado (`30`, `60`, `90`, `120`, `150`).
- **Fecha de Vencimiento (`date_due`):** Fecha máxima de pago sin protesto.
- **N° Único (Banco) (`unique_number`):** Código numérico asignado por el banco al ingresar a cobranza/descuento (necesario para que el cliente pague en ventanilla).
- **Valor Banco (Interno) (`internal_bank_number`):** Número de control interno del banco para conciliaciones.
- **Fecha de Pago (`date_payment`):** Fecha en la que el cliente o banco canceló la letra (se llena al presionar *Registrar Pago*).
- **Fecha de Protesto (`protest_date`):** Fecha en la que el banco ejecutó el protesto. Aparece (solo lectura) únicamente cuando la letra fue protestada.
- **Nota de Débito (Gastos) (`debit_note_id`):** Vínculo a la nota de débito generada automáticamente por los gastos y costas del protesto.

##### Importes:
- **Importe Total (`amount_total`):** Valor nominal de la letra.
- **Importe Pagado (`amount_paid`):** Suma acumulada de amortizaciones.
- **Saldo Pendiente (`amount_residual`):** Valor líquido pendiente de cobro.

---

### 3.3 Ciclo de Vida y Transición de Estados (Clic a Clic)

Cada letra sigue una secuencia estricta de botones de acción:

```
[Borrador] ➔ (Enviar al Cliente) ➔ [Enviada] ➔ (Registrar Firma + Adjuntar) ➔ [Firmada] ➔ (Enviar al Banco) ➔ [En Banco] ➔ (Registrar Pago) ➔ [Pagada]
```

#### Paso 1: Enviar al Cliente (`draft` ➔ `sent`)
1. Dentro del formulario de la letra en estado **Borrador**, haz clic en el botón **Enviar al Cliente**.
2. El estado cambiará a **Enviada**. La letra puede imprimirse en PDF mediante el botón **Imprimir Letra**.

#### Paso 2: Registrar Firma y Adjuntar Documento (`sent` ➔ `signed`)
1. Una vez que el cliente devuelve la letra física con firma y sello oficial, sube el **archivo PDF** en el campo **Cargar Letra Firmada (PDF)** (*Datos Principales*). El sistema **solo acepta PDF**; si subes otro formato, lo rechaza.
   > *También puede adjuntarlo desde el panel lateral de comentarios (**Chatter**), pero el campo dedicado es el método recomendado.*
2. Mientras no exista documento cargado, verás un aviso azul y el botón **Registrar Firma** **no aparecerá** (no podrás registrar la firma).
3. Al cargar el documento, aparecerá un aviso verde y el botón **Registrar Firma** se habilitará.
4. Haz clic en **Registrar Firma**. El estado cambiará a **Firmada**.

#### Paso 3: Enviar al Banco (`signed` ➔ `in_bank`)
1. Haz clic en el botón **Enviar al Banco**.
2. **Validación de Seguridad:** Si el instrumento es `Letra de Cambio` y no has cargado la letra firmada (campo `signed_document` o adjunto en el chatter), el sistema mostrará un bloqueo de seguridad impidiendo el envío.
3. Al validar la presencia del adjunto, la letra pasará al estado **En Banco**.

#### Paso 4: Registrar Pago (`in_bank` ➔ `paid`)
1. Cuando el banco confirma la cancelación por parte del cliente:
2. Haz clic en el botón **Registrar Pago**.
3. El estado cambiará a **Pagada**, se registrará la fecha de pago actual y el **Saldo Pendiente** quedará en `0.00` (el *Importe Pagado* se iguala al *Importe Total*).

---

## 4. OPERACIÓN 2: MODALIDAD "CABAL" (CANJE 100% FACTURA)

### ¿Qué es Cabal?
Es una modalidad especial utilizada para clientes corporativos donde las facturas se canjean al 100% en la plataforma bancaria (Telecrédito) sin requerir la emisión, firma ni sello físico de una letra en papel. El cliente solo **confirma el vencimiento por correo**.

### ¿Dónde se configura?
**No se configura en Ajustes**: se elige por operación con el campo **Tipo de Instrumento**. Además, puede dejar a un cliente fijo como Cabal:
1. Ve a **Ventas/Contabilidad** -> **Clientes** -> abre el cliente.
2. Pestaña **Letras de Cambio** -> marca la casilla **Cliente Cabal**.
3. Guarda. Desde ese momento, al generar letras desde sus facturas el sistema propondrá automáticamente `Cabal`.

### 🖱️ Guía Clic a Clic para Operaciones Cabal:
1. Ve al menú **Letras de Cambio** -> **Operaciones** -> **Operaciones Cabal** (o crea una letra y cambia el campo **Tipo de Instrumento** a `Cabal`).
2. Haz clic en **Crear**.
3. Selecciona el **Cliente**.
4. El campo **Tipo de Instrumento** vendrá predeterminado en `Cabal`.
5. En la pestaña **Facturas Asociadas**, agrega la factura confirmada enviada por correo.
6. Haz clic en **Guardar**.
7. En esta modalidad, **no se muestra** el campo de documento firmado ni el botón **Registrar Firma**; puedes enviar al banco directamente con **Enviar al Banco**.

---

## 5. OPERACIÓN 3: AGRUPACIÓN Y ENVÍO DE PLANILLAS AL BANCO

### ¿Para qué sirve?
Agrupa un conjunto de letras firmadas para enviarlas físicamente y electrónicamente a una entidad bancaria (BCP, Scotiabank, BBVA) para su descuento o cobranza.

### Explicación Campo por Campo de la Planilla (`l10n.pe.letra.planilla`):
- **N° Planilla (`name`):** Secuencia correlativa de la planilla (ejemplo: `PLAN/2026/00001`).
- **Banco (`bank_id`):** Entidad bancaria receptora.
- **Fecha (`date`):** Fecha de armador y presentación de la planilla.
- **Estado (`state`):** `Borrador` ➔ `Enviada al Banco` ➔ `Confirmada`.
- **Importe Total (`amount_total`):** Suma automática del importe de todas las letras incluidas.
- **Cant. Letras (`letra_count`):** Número total de letras en la planilla.

### 🖱️ Guía Clic a Clic para crear y procesar una Planilla:
1. Ve al menú **Letras de Cambio** -> **Operaciones** -> **Planillas**.
2. Haz clic en **Crear**.
3. Selecciona el **Banco** (ejemplo: `Banco de Crédito del Perú - BCP`).
4. En la tabla **Letras**, haz clic en **Agregar una línea** y selecciona todas las letras en estado `Firmada` o `Borrador` que se enviarán al banco.
5. Haz clic en **Guardar**.
6. Haz clic en **Enviar al Banco** para pasar la planilla a estado `Enviada al Banco`. Luego, abre cada letra y usa **Enviar al Banco** en ella (valida el documento firmado), de modo que quede en estado `En Banco` asignada a esta planilla.
7. Haz clic en los botones de reporte en la parte superior:
   - **Imprimir Planilla:** Genera el documento resumen en PDF con la lista de letras para la firma del Gerente.
   - **Imprimir Letras:** Descarga en un solo archivo PDF todas las letras incluidas en la planilla.

---

## 6. SEGUIMIENTO 1: PROTESTO DE LETRAS DE CAMBIO

### ¿Cuándo ocurre un Protesto?
Si al vencimiento de la letra (más 8 días de gracia concedidos por el banco), el cliente no ha cancelado la deuda en el banco (Día 9), el banco debita el dinero de la cuenta de Curpisco y la letra entra en **Protesto** (Estado `protested`).

### 🖱️ Guía Clic a Clic para registrar un Protesto:
1. Abre la letra que se encuentra en estado **En Banco**.
2. Haz clic en el botón rojo **Registrar Protesto**.
3. Se abrirá la ventana emergente de registro:
   - **Fecha de Protesto:** Fecha en la que el banco ejecutó el devoto/protesto.
   - **Monto Protestado:** Importe nominal no pagado.
   - **Gastos y Costas:** Gastos bancarios y notariales cobrados por el banco (ejemplo: `150.00`).
   - **Total:** Suma automática del monto protestado + gastos.
4. Haz clic en **Guardar / Confirmar**.

### ⚡ EFECTOS AUTOMÁTICOS DEL PROTESTO EN EL SISTEMA:
1. **Cambio de Estado:** La letra pasa automáticamente a estado **Protestada** y registra la **Fecha de Protesto**.
2. **Generación de Nota de Débito:** Si se ingresó un monto en **Gastos y Costas**, el sistema crea automáticamente un borrador de **Nota de Débito** (`account.move`) en el diario de ventas a nombre del cliente por el concepto de *Gastos y Costas de Protesto Bancario*. El documento queda vinculado en el campo **Nota de Débito (Gastos)** de la letra.
   > *Si los gastos son `0.00`, no se genera nota de débito.*
3. **Bloqueo Comercial Automático:**
   - El cliente y todas las empresas de su **Grupo Empresarial** quedan marcados con `commercial_blocked = True`.
   - Si un vendedor intenta confirmar un **Pedido de Venta** (`sale.order.action_confirm`) para este cliente o grupo, Odoo **bloqueará la transacción** mostrando el mensaje de error:
     > *"No se puede confirmar el pedido. El cliente X está bloqueado comercialmente. Motivo: Tiene letras protestadas pendientes de regularización."*

### 🖱️ Guía Clic a Clic para Regularizar un Protesto:
1. Ve al menú **Letras de Cambio** -> **Seguimiento** -> **Protestos**.
2. Selecciona el protesto en estado `Pendiente`.
3. Cuando el cliente paga el protesto y la nota de débito de gastos, haz clic en **Regularizar**.
4. Selecciona el **Tipo de Regularización** (`Pago`, `Renovación`, `Acuerdo`) e ingresa la **Fecha de Regularización**.
5. Al regularizar todos los protestos pendientes, el bloqueo comercial sobre el cliente se **levantará automáticamente**.

---

## 7. SEGUIMIENTO 2: RENOVACIÓN DE LETRAS DE CAMBIO

### ¿Cuándo se aplica una Renovación?
Cuando un cliente no puede pagar el 100% de una letra al vencimiento y negocia pagar un porcentaje inicial (ejemplo: 40%) y diferir el saldo en una **nueva letra**.

### Regla Bancaria Inflexible (RN-004):
El plazo de la nueva letra generada por renovación es **estrictamente de 30 días** (impuesto por el sistema bancario peruano).

### 🖱️ Guía Clic a Clic para ejecutar una Renovación:
1. Abre la letra que se encuentra en estado **En Banco** o **Protestada**.
2. Haz clic en el botón amarillo **Renovar**.
3. Se abrirá el wizard **Asistente de Renovación de Letra**:
   - **Monto Original:** Muestra el saldo de la letra origen.
   - **Intereses:** Ingresa los intereses bancarios cobrados por la prórroga (ejemplo: `50.00`).
   - **Gastos:** Gastos administrativos (ejemplo: `20.00`).
   - **Nuevo Monto:** Muestra el monto computable de la nueva letra.
   - **Fecha de Emisión:** Fecha de la renovación.
   - **Plazo Renovación:** Fijado automáticamente en `30 Días (Obligatorio Banco)`.
   - **Nueva Fecha de Vencimiento:** Calculada automáticamente a 30 días de la emisión.
   - **Motivo de Renovación:** Texto explicativo del acuerdo.
4. Haz clic en **Renovar Letra**.

### ⚡ EFECTOS AUTOMÁTICOS DE LA RENOVACIÓN:
1. La letra original pasa al estado **Renovada** (cerrando su ciclo activo).
2. Se crea automáticamente una **nueva Letra de Cambio** por el monto del saldo a 30 días de vencimiento.
3. Se establece un vínculo de trazabilidad bidireccional (`renovacion_origin_id` y `renovacion_destino_ids`).

---

## 8. SEGUIMIENTO 3: PROYECCIÓN SEMANAL DE COBRANZA (PIVOT / GRÁFICO)

Reemplaza por completo las plantillas manuales de Excel para la reunión ejecutiva de los lunes.

### 🖱️ Guía Clic a Clic para consultar la Proyección:
1. Ve al menú **Letras de Cambio** -> **Seguimiento** -> **Proyección Semanal**.
2. Se cargará la vista de **Tabla Dinámica (Pivot)**:
   - **Filas:** Vendedor (`salesperson_id`) ➔ Cliente (`partner_id`).
   - **Columnas:** Fecha de Vencimiento agrupada por **Semana** (`date_due:week`).
   - **Medidas:** Importe Total y Saldo Pendiente.
3. Para cambiar a gráfico, haz clic en el icono de **Gráfico de Barras** (arriba a la derecha).
4. Puedes aplicar filtros dinámicos por Banco, Estado o Vendedor usando la barra de búsqueda superior.

---

## 9. SEGUIMIENTO 4: ENVÍO MASIVO POR EMAIL Y EXPORTACIÓN EXCEL

### 🖱️ Guía Clic a Clic para exportar y enviar el reporte semanal:
1. Ve a **Letras de Cambio** -> **Operaciones** -> **Enviar Letras por Email** (o **Reportes** -> **Exportar Resumen Excel / Email**).
2. En la ventana del wizard **Enviar Letras por Email**:
   - **Desde / Hasta:** Define el rango de fechas de emisión a consultar.
   - **Enviar a:** Dirección de correo electrónico destino (autocompletado con la configuración global).
   - **Filtrar por Estado:** Selecciona el estado (`En Banco`, `Protestada`, etc.).
   - **Incluir PDF por letra:** Marca `True` si deseas adjuntar los PDFs individuales de cada letra.
   - **Incluir Excel resumen:** Marca `True` para generar la hoja de cálculo profesional.
3. Haz clic en **Enviar Letras**.
4. El sistema enviará un **correo electrónico real** con el archivo `.xlsx` (estilos ejecutivos, formato de moneda y totales) y, si lo marcaste, los PDFs de cada letra adjuntos. El envío queda registrado en el **Chatter** de la primera letra del lote para trazabilidad.
   > *Para que el correo salga, el servidor de correo saliente debe estar configurado en Odoo (Ajustes -> Correo saliente).*

---

## 10. MATRIZ DE SEGURIDAD, BLOQUEOS COMERCIALES Y REGLAS DE NEGOCIO

### Matriz de Transición de Estados:

| Estado Actual | Botón Disponible | Siguiente Estado | Requisito / Validación de Seguridad |
|---|---|---|---|
| `draft` (Borrador) | Enviar al Cliente | `sent` | Ninguno. |
| `sent` (Enviada) | Registrar Firma | `signed` | **Obligatorio:** PDF firmado cargado en `signed_document` (solo tipo Letra). El botón no aparece hasta cargarlo. |
| `signed` (Firmada) | Enviar al Banco | `in_bank` | **Obligatorio:** Documento firmado cargado (campo o chatter) si es tipo Letra. |
| `in_bank` (En Banco) | Registrar Pago | `paid` | Registra la fecha de cobro final y deja el saldo en `0.00`. |
| `in_bank` (En Banco) | Registrar Protesto | `protested` | Crea registro de protesto y Nota de Débito automática (si hay gastos). |
| `in_bank` / `protested` | Renovar | `renewed` | Genera nueva letra a 30 días fijados por el banco. |

### Reglas de Negocio Aplicadas en el Módulo:

- **RN-001 (Facturas asociadas):** Solo se pueden asociar a una letra facturas de cliente, **publicadas** y **no pagadas**, y todas deben ser del **mismo cliente**. El sistema bloquea el guardado si no se cumple.
- **RN-003 (Firma obligatoria):** No se puede registrar la firma ni enviar al banco una letra tipo `Letra de Cambio` sin el PDF firmado cargado. El campo solo acepta archivos PDF.
- **RN-004 (Plazo de renovación):** Toda renovación se genera forzosamente a **30 días**.
- **RN-005 (Nota de débito por protesto):** Al protestar con gastos, se genera la nota de débito al cliente.
- **RN-007 (Techo agregado):** La suma de líneas de crédito de todos los grupos no puede superar el **Techo Agregado** de la compañía, salvo que el grupo tenga marcada la **Aprobación de Excepción**.
- **RN-009 (Cabal):** Las operaciones tipo `Cabal` no exigen documento firmado.

### Reglas de Bloqueo Comercial en Pedidos de Venta (`sale.order`):
- **Regla 1 (Protestos):** Si `partner_id.commercial_blocked == True`, el sistema impide la confirmación de la orden.
- **Regla 2 (Exceso de Crédito):** Si el cliente pertenece a un Grupo Empresarial y `credit_available < order.amount_total`, el sistema impide la confirmación de la orden indicando el saldo disponible real.

### Recordatorios Automáticos de Vencimiento:
El sistema ejecuta diariamente una acción programada (**Letras: recordatorio de vencimiento**) que crea una **actividad** para las letras `En Banco` que vencen en los próximos 7 días, reemplazando el aviso manual por WhatsApp. Puedes consultarlas en el icono de **Actividades** ⏰ del menú superior.

---

## 11. CATÁLOGO COMPLETO DE REPORTES Y RUTAS DE ACCESO AL MENÚ

El módulo incluye un conjunto de **6 reportes oficiales** (PDF impresos, Hoja de cálculo Excel profesional y Tableros Analíticos interactivos).

---

### 📌 1. Reporte PDF: Estado de Cuenta de Crédito y Letras (`action_report_estado_cuenta_partner`)
- **Descripción:** Estado de cuenta consolidado del cliente o su grupo empresarial.
- **Contenido:** Razón social del cliente/RUC, **Línea de Crédito aprobada vs utilizada vs disponible**, estado de bloqueo comercial, tabla de todas las letras activas (emisión, vencimiento, banco, N° único y saldo) y alertas de protestos.
- **🗺️ Ruta del Menú / Clic a Clic:**
  1. Ve a **Ventas** (o **Contabilidad**) ➔ **Clientes**.
  2. Haz clic en la ficha del cliente deseado.
  3. En la barra superior, haz clic en el menú **`Imprimir`** 🖨️ (icono de impresora) ➔ selecciona **`Estado de Cuenta de Letras`**.

---

### 📌 2. Reporte Excel (.xlsx): Resumen Ejecutivo de Cartera (`action_enviar_letras_wizard`)
- **Descripción:** Hoja de cálculo ejecutiva generada en Excel con estilos corporativos (`openpyxl`).
- **Contenido:** Formato con encabezados azul oscuro (`#2C3E50`), texto en blanco, bordes finos, formateo de moneda (`#,##0.00`), totales automáticos y bloque informativo al pie.
- **🗺️ Ruta del Menú / Clic a Clic:**
  - **Opción Directa (Nuevo Menú):** Ve a **Letras de Cambio** ➔ **Reportes** ➔ **Exportar Resumen Excel / Email**.
  - **Opción en Lista de Letras:** Ve a **Letras de Cambio** ➔ **Operaciones** ➔ **Letras de Cambio** ➔ selecciona las letras ➔ rueda dentada de **Acciones** ➔ **Enviar por Email**.
  1. En el wizard, selecciona la fecha *Desde / Hasta* y el correo destino.
  2. Marca la casilla ☑️ **`Incluir Excel resumen`**.
  3. Haz clic en el botón **`Enviar`**.

---

### 📌 3. Reporte Analítico: Proyección Semanal en Tabla Dinámica (Pivot) (`action_proyeccion_cobranza`)
- **Descripción:** Matriz Pivot interactiva diseñada para la reunión ejecutiva de los lunes.
- **Contenido:** Vencimientos semanales cruzados por Vendedor comercial (`salesperson_id`) y Cliente (`partner_id`), mostrando importe nominal total y saldo pendiente.
- **🗺️ Ruta del Menú / Clic a Clic:**
  - Ve a **Letras de Cambio** ➔ **Reportes** ➔ **Proyección Semanal (Pivot)**.
  - *O alternativamente:* **Letras de Cambio** ➔ **Seguimiento** ➔ **Proyección Semanal**.

---

### 📌 4. Reporte Analítico: Gráfico de Cartera por Vendedor (`view_letra_graph`)
- **Descripción:** Gráfico de barras interactivo de proyección comercial por vendedor.
- **Contenido:** Muestra el monto total en cobranza/riesgo asignado a cada vendedor (Donato, Segundo, Roberto, etc.).
- **🗺️ Ruta del Menú / Clic a Clic:**
  1. Ve al menú **Letras de Cambio** ➔ **Reportes** ➔ **Proyección Semanal (Pivot)**.
  2. En la esquina superior derecha (al lado de la barra de búsqueda), haz clic en el **icono de Gráfico de Barras** 📊.

---

### 📌 5. Reporte PDF: Letra de Cambio Oficial (`action_report_letra`)
- **Descripción:** Formato impreso formal de la letra de cambio según normativa peruana.
- **Contenido:** Razón social del Girador (Curpisco), dirección fiscal, cliente (Aceptante), importe formal en soles (`S/`), fecha de emisión, fecha de vencimiento, banco asignado, tabla de facturas asociadas y firmas para **Girador** y **Aceptación/Sello del Cliente**.
- **🗺️ Ruta del Menú / Clic a Clic:**
  1. Ve a **Letras de Cambio** ➔ **Operaciones** ➔ **Letras de Cambio**.
  2. Abre el formulario de la letra que deseas imprimir.
  3. Haz clic en el botón **`Imprimir Letra`** (en la barra superior del formulario) o en **`Imprimir`** 🖨️ ➔ **`Letra de Cambio`**.

---

### 📌 6. Reporte PDF: Planilla de Envío al Banco (`action_report_letra_planilla`)
- **Descripción:** Documento agrupador impreso para presentar a ventanilla del banco (BCP, Scotiabank, BBVA).
- **Contenido:** Banco receptor, fecha de envío, relación detallada de letras (N° Letra, Cliente, Importe, Vencimiento, Estado), total acumulado, cantidad de documentos y firmas de **Entregado por** (Gerencia) y **Recibido por** (Ventanilla del Banco).
- **🗺️ Ruta del Menú / Clic a Clic:**
  1. Ve a **Letras de Cambio** ➔ **Operaciones** ➔ **Planillas**.
  2. Abre la planilla bancaria.
  3. Haz clic en **`Imprimir Planilla`** (para la planilla firmada por Gerencia) o en **`Imprimir Letras`** (para descargar en un único PDF el paquete completo de letras incluidas).


