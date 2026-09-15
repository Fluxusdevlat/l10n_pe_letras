from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


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
    protest_date = fields.Date(string='Fecha de Protesto', readonly=True,
                               tracking=True)
    debit_note_id = fields.Many2one('account.move',
                                    string='Nota de Débito (Gastos)',
                                    readonly=True, copy=False)

    renovacion_origin_id = fields.Many2one('l10n.pe.letra',
                                           string='Letra Origen (Renovación)',
                                           readonly=True)
    renovacion_destino_ids = fields.One2many('l10n.pe.letra',
                                             'renovacion_origin_id',
                                             string='Letras Destino (Renovación)')
    is_renovacion = fields.Boolean(string='Es Renovación', default=False)
    signed_document = fields.Binary(string='Documento Firmado (PDF / Imagen)',
                                    attachment=True, copy=False)
    signed_filename = fields.Char(string='Nombre Archivo Firmado', copy=False)
    can_sign = fields.Boolean(string='Puede Firmar', compute='_compute_can_sign')

    notes = fields.Text(string='Observaciones')

    @api.depends('state', 'instrument_type', 'signed_document')
    def _compute_can_sign(self):
        for r in self:
            if r.instrument_type == 'cabal':
                r.can_sign = True
            else:
                r.can_sign = bool(r.signed_document)

    _sql_constraints = [
        ('name_unique', 'unique(name, company_id)',
         'El número de letra debe ser único por compañía'),
    ]

    @api.onchange('partner_id')
    def _onchange_partner_id_days_term(self):
        if self.partner_id and self.partner_id.letra_days_term:
            self.days_term = self.partner_id.letra_days_term

    @api.onchange('line_ids')
    def _onchange_line_ids_amount_total(self):
        if self.line_ids:
            self.amount_total = sum(self.line_ids.mapped('amount'))

    @api.constrains('line_ids', 'partner_id')
    def _check_invoices_same_partner(self):
        for letra in self:
            for line in letra.line_ids:
                if not letra.partner_id:
                    continue
                if line.move_id.partner_id.commercial_partner_id != \
                        letra.partner_id.commercial_partner_id:
                    raise ValidationError(_(
                        'Todas las facturas asociadas deben pertenecer al '
                        'mismo cliente de la letra.'))

    @api.constrains('line_ids')
    def _check_invoices_open(self):
        for letra in self:
            for line in letra.line_ids:
                move = line.move_id
                if move.move_type not in ('out_invoice', 'out_refund'):
                    raise ValidationError(_(
                        'Solo se pueden asociar facturas de cliente a una letra.'))
                if move.state != 'posted':
                    raise ValidationError(_(
                        'La factura %s no está publicada.') % move.name)
                if move.payment_state in ('paid', 'reversed'):
                    raise ValidationError(_(
                        'La factura %s ya está pagada y no puede incluirse '
                        'en una letra.') % move.name)

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('l10n.pe.letra') or _('New')
        return super().create(vals_list)

    def action_sent(self):
        self.state = 'sent'

    def action_signed_warning(self):
        raise UserError(_(
            'Para poder registrar la firma, primero debe cargar la letra firmada '
            'en el campo "Cargar Letra Firmada (PDF / Foto)".'
        ))

    def action_signed(self):
        for r in self:
            if r.instrument_type == 'letra' and not r.signed_document:
                raise UserError(_(
                    'Debe cargar la imagen o PDF de la letra firmada en el campo "Documento Firmado" '
                    'antes de poder registrar la firma.'
                ))
            r.state = 'signed'

    def action_send_to_bank(self):
        for r in self:
            if r.instrument_type == 'letra' and not r.signed_document:
                attachments = self.env['ir.attachment'].search_count([
                    ('res_model', '=', 'l10n.pe.letra'),
                    ('res_id', '=', r.id)
                ])
                if not attachments and not r.message_main_attachment_id:
                    raise UserError(_(
                        'No se puede enviar la letra al banco sin cargar el documento '
                        'firmado en el campo "Documento Firmado" (o en el chatter).'
                    ))
            r.state = 'in_bank'

    def action_paid(self):
        for r in self:
            r.write({
                'state': 'paid',
                'date_payment': fields.Date.today(),
                'amount_paid': r.amount_total,
            })

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

    @api.model
    def _cron_notify_due_letras(self):
        today = fields.Date.today()
        target = today + timedelta(days=7)
        activity_type = self.env.ref('mail.mail_activity_data_todo',
                                     raise_if_not_found=False)
        if not activity_type:
            return
        letras = self.search([
            ('state', '=', 'in_bank'),
            ('date_due', '>=', today),
            ('date_due', '<=', target),
        ])
        for letra in letras:
            existing = self.env['mail.activity'].search_count([
                ('res_model', '=', 'l10n.pe.letra'),
                ('res_id', '=', letra.id),
                ('activity_type_id', '=', activity_type.id),
            ])
            if existing:
                continue
            letra.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=letra.date_due,
                summary=_('Letra %s próxima a vencer') % letra.name,
                note=_('Contactar al cliente %s por la letra %s que vence '
                       'el %s.') % (letra.partner_id.name, letra.name,
                                    letra.date_due),
            )

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

    _sql_constraints = [
        ('check_amount_positive', 'CHECK(amount > 0)',
         'El monto aplicado debe ser mayor a cero'),
    ]
