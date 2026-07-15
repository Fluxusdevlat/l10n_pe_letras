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

    date_emission = fields.Date(string='Fecha de Emisión',
                                default=fields.Date.context_today,
                                required=True, tracking=True)
    date_due = fields.Date(string='Fecha de Vencimiento',
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

    notes = fields.Text(string='Observaciones')

    _sql_constraints = [
        ('name_unique', 'unique(name, company_id)',
         'El número de letra debe ser único por compañía'),
    ]

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

    def action_signed(self):
        self.state = 'signed'

    def action_send_to_bank(self):
        self.state = 'in_bank'

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

    _sql_constraints = [
        ('check_amount_positive', 'CHECK(amount > 0)',
         'El monto aplicado debe ser mayor a cero'),
    ]
