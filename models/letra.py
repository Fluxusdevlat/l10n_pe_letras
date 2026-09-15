import base64

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date


class Letra(models.Model):
    _name = 'l10n.pe.letra'
    _description = 'Letra de Cambio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_emission desc, id desc'

    name = fields.Char(string='N° Letra', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Cliente',
                                 required=True, tracking=True)
    bank_id = fields.Many2one('res.bank', string='Banco',
                              tracking=True)
    amount_total = fields.Monetary(string='Importe Total', required=True,
                                   tracking=True)
    amount_paid = fields.Monetary(string='Importe Pagado', default=0.0)
    amount_residual = fields.Monetary(string='Saldo Pendiente',
                                      compute='_compute_amount_residual',
                                      store=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('signed', 'Firmada'),
        ('in_bank', 'En Banco'),
        ('protested', 'Protestada'),
        ('cancelled', 'Cancelada'),
        ('renewed', 'Renovada'),
        ('paid', 'Pagada'),
    ], string='Estado', default='draft', tracking=True)

    tipo = fields.Selection([
        ('emission', 'Emisión'),
        ('canje', 'Canje'),
    ], string='Tipo', default='emission', required=True, tracking=True)

    instrument_type = fields.Selection([
        ('letra', 'Letra de Cambio'),
        ('cabal', 'Cabal'),
    ], string='Tipo de Instrumento', default='letra', required=True, tracking=True)

    days_term = fields.Selection([
        ('30', '30 Días'),
        ('60', '60 Días'),
        ('90', '90 Días'),
        ('120', '120 Días'),
        ('150', '150 Días (Anticipo)'),
    ], string='Plazo en Días', default='30', required=True, tracking=True)

    unique_number = fields.Char(string='N° Único (Banco)', tracking=True)
    internal_bank_number = fields.Char(string='Valor Banco (Interno)', tracking=True)
    salesperson_id = fields.Many2one('res.users', string='Vendedor',
                                    related='partner_id.user_id', store=True)

    date_emission = fields.Date(string='Fecha de Emisión',
                                default=fields.Date.context_today,
                                required=True, tracking=True)
    date_due = fields.Date(string='Fecha de Vencimiento',
                           compute='_compute_date_due', store=True, readonly=False,
                           required=True, tracking=True)
    date_payment = fields.Date(string='Fecha de Pago',
                               tracking=True)

    line_ids = fields.One2many('l10n.pe.letra.line', 'letra_id',
                               string='Facturas Asociadas')
    planilla_id = fields.Many2one('l10n.pe.letra.planilla',
                                  string='Planilla', readonly=True)
    protesto_ids = fields.One2many('l10n.pe.letra.protesto', 'letra_id',
                                   string='Protestos')
    protesto_count = fields.Integer(string='Cant. Protestos',
                                    compute='_compute_protesto_count')

    renovacion_origin_id = fields.Many2one('l10n.pe.letra',
                                           string='Letra Origen (Renovación)',
                                           readonly=True)
    renovacion_destino_ids = fields.One2many('l10n.pe.letra',
                                             'renovacion_origin_id',
                                             string='Letras Destino (Renovación)')
    is_renovacion = fields.Boolean(string='Es Renovación', default=False)

    signed_document = fields.Binary(string='Documento Firmado (PDF)',
                                    attachment=True, copy=False)
    signed_filename = fields.Char(string='Nombre Archivo Firmado', copy=False)
    can_sign = fields.Boolean(string='Puede Firmar',
                              compute='_compute_can_sign')

    notes = fields.Text(string='Observaciones')

    _name_unique = models.Constraint(
        'UNIQUE(name, company_id)',
        'El número de letra debe ser único por compañía')

    @api.onchange('partner_id')
    def _onchange_partner_id_days_term(self):
        if self.partner_id and self.partner_id.letra_days_term:
            self.days_term = self.partner_id.letra_days_term

    @api.onchange('line_ids')
    def _onchange_line_ids_amount_total(self):
        if self.line_ids:
            self.amount_total = sum(self.line_ids.mapped('amount'))

    def action_open_generate_wizard(self):
        self.ensure_one()
        context = dict(self.env.context)
        if self.partner_id:
            context['default_partner_id'] = self.partner_id.id
        if self.line_ids:
            context['default_invoice_ids'] = [(6, 0, self.line_ids.mapped('move_id').ids)]
        return {
            'name': _('Generar Letras desde Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra.generate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    @api.depends('date_emission', 'days_term')
    def _compute_date_due(self):
        from datetime import timedelta
        for r in self:
            if r.date_emission and r.days_term:
                try:
                    days = int(r.days_term)
                    r.date_due = r.date_emission + timedelta(days=days)
                except ValueError:
                    pass
            if not r.date_due:
                r.date_due = fields.Date.today()


    @api.depends('amount_total', 'amount_paid')
    def _compute_amount_residual(self):
        for r in self:
            r.amount_residual = r.amount_total - r.amount_paid

    def _compute_protesto_count(self):
        for r in self:
            r.protesto_count = len(r.protesto_ids)

    @api.depends('instrument_type', 'signed_document')
    def _compute_can_sign(self):
        for r in self:
            if r.instrument_type == 'cabal':
                r.can_sign = True
            else:
                r.can_sign = bool(r.signed_document)

    @api.constrains('signed_document', 'signed_filename')
    def _check_signed_document_pdf(self):
        for letra in self:
            if not letra.signed_document:
                continue
            filename = (letra.signed_filename or '').lower()
            if filename and not filename.endswith('.pdf'):
                raise ValidationError(_(
                    'Solo se permite subir la letra firmada en formato PDF.'))
            try:
                content = base64.b64decode(letra.signed_document)
            except Exception:
                raise ValidationError(_(
                    'El archivo cargado no es un PDF válido.'))
            if not content.startswith(b'%PDF'):
                raise ValidationError(_(
                    'Solo se permite subir la letra firmada en formato PDF.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('l10n.pe.letra') or _('New')
        return super().create(vals_list)

    def action_sent(self):
        self.state = 'sent'

    def action_signed(self):
        for r in self:
            if r.instrument_type == 'letra' and not r.signed_document:
                raise UserError(_(
                    'Debe cargar el documento firmado (PDF) en el campo '
                    '"Cargar Letra Firmada (PDF)" antes de registrar la firma.'
                ))
            r.state = 'signed'

    def action_send_to_bank(self):
        for r in self:
            if r.instrument_type == 'letra' and not r.signed_document:
                raise UserError(_(
                    'No se puede enviar la letra a banco sin cargar el '
                    'documento firmado (PDF) del cliente.'
                ))
            r.state = 'in_bank'

    def action_paid(self):
        self.state = 'paid'
        self.date_payment = fields.Date.today()

    def action_cancel(self):
        self.state = 'cancelled'

    def action_renew(self):
        self.ensure_one()

        return {
            'name': _('Renovar Letra'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra.renovacion.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_letra_origin_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_amount_total': self.amount_residual,
            },
        }

    def action_register_protest(self):
        self.ensure_one()
        return {
            'name': _('Registrar Protesto'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra.protesto',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_letra_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_residual,
            },
        }

    def action_print_letra(self):
        self.ensure_one()
        return self.env.ref('l10n_pe_letras.action_report_letra').report_action(self)

    def action_view_signed_document(self):
        self.ensure_one()
        if not self.signed_document:
            raise UserError(_('Aún no se ha cargado la letra firmada.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/l10n.pe.letra/%s/signed_document/%s?download=true'
                   % (self.id, self.signed_filename or 'letra_firmada.pdf'),
            'target': 'new',
        }

    def name_get(self):
        res = []
        for r in self:
            name = r.name
            if r.partner_id:
                name = f'{name} - {r.partner_id.name}'
            res.append((r.id, name))
        return res


class LetraLine(models.Model):
    _name = 'l10n.pe.letra.line'
    _description = 'Línea de Letra - Factura Asociada'

    letra_id = fields.Many2one('l10n.pe.letra', string='Letra',
                               required=True, ondelete='cascade')
    move_id = fields.Many2one('account.move', string='Factura',
                              domain=[('move_type', 'in', ('out_invoice', 'out_refund'))],
                              required=True)
    partner_id = fields.Many2one(related='move_id.partner_id', store=True)
    amount = fields.Monetary(string='Monto Aplicado', required=True)
    amount_residual = fields.Monetary(string='Saldo Factura',
                                      related='move_id.amount_residual')
    currency_id = fields.Many2one('res.currency',
                                  related='move_id.currency_id')
    date_invoice = fields.Date(string='Fecha Factura',
                               related='move_id.invoice_date')

    @api.onchange('move_id')
    def _onchange_move_id_amount(self):
        if self.move_id and not self.amount:
            self.amount = self.move_id.amount_residual

    _check_amount_positive = models.Constraint(
        'CHECK(amount > 0)',
        'El monto aplicado debe ser mayor a cero')
