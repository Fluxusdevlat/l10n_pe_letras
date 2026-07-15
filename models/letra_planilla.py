from odoo import api, fields, models, _


class LetraPlanilla(models.Model):
    _name = 'l10n.pe.letra.planilla'
    _description = 'Planilla de Letras para Banco'
    _order = 'date desc, id desc'

    name = fields.Char(string='N° Planilla', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    bank_id = fields.Many2one('res.bank', string='Banco', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today,
                       required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada al Banco'),
        ('confirmed', 'Confirmada'),
    ], string='Estado', default='draft', tracking=True)

    letra_ids = fields.One2many('l10n.pe.letra', 'planilla_id',
                                string='Letras', domain=[('state', '!=', 'cancelled')])
    letra_count = fields.Integer(string='Cant. Letras',
                                 compute='_compute_letra_count')
    amount_total = fields.Monetary(string='Importe Total',
                                   compute='_compute_amount_total')

    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)

    notes = fields.Text(string='Observaciones')

    @api.depends('letra_ids')
    def _compute_letra_count(self):
        for r in self:
            r.letra_count = len(r.letra_ids)

    @api.depends('letra_ids', 'letra_ids.amount_total')
    def _compute_amount_total(self):
        for r in self:
            r.amount_total = sum(r.letra_ids.mapped('amount_total'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'l10n.pe.letra.planilla') or _('New')
        return super().create(vals_list)

    def action_send(self):
        self.state = 'sent'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_print_planilla(self):
        return self.env.ref(
            'l10n_pe_letras.action_report_letra_planilla'
        ).report_action(self)

    def action_print_letras(self):
        letras = self.letra_ids
        return self.env.ref(
            'l10n_pe_letras.action_report_letra'
        ).report_action(letras)
