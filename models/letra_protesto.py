from odoo import api, fields, models, _


class LetraProtesto(models.Model):
    _name = 'l10n.pe.letra.protesto'
    _description = 'Protesto de Letra'
    _order = 'date_protest desc, id desc'

    name = fields.Char(string='N° Protesto', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    letra_id = fields.Many2one('l10n.pe.letra', string='Letra',
                               required=True)
    partner_id = fields.Many2one(related='letra_id.partner_id',
                                 string='Cliente', store=True)
    date_protest = fields.Date(string='Fecha de Protesto',
                               default=fields.Date.context_today,
                               required=True)
    amount = fields.Monetary(string='Monto Protestado', required=True)
    gastos = fields.Monetary(string='Gastos y Costas', default=0.0)
    total = fields.Monetary(string='Total',
                            compute='_compute_total', store=True)

    currency_id = fields.Many2one('res.currency',
                                  related='letra_id.currency_id')
    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company)

    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('resolved', 'Regularizado'),
    ], string='Estado', default='pending')

    resolution_date = fields.Date(string='Fecha de Regularización')
    resolution_type = fields.Selection([
        ('payment', 'Pago'),
        ('renewal', 'Renovación'),
        ('agreement', 'Acuerdo'),
        ('other', 'Otro'),
    ], string='Tipo de Regularización')

    debit_note_id = fields.Many2one('account.move', string='Nota de Débito (Gastos)',
                                  readonly=True)
    notes = fields.Text(string='Observaciones')

    @api.depends('amount', 'gastos')
    def _compute_total(self):
        for r in self:
            r.total = r.amount + r.gastos

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'l10n.pe.letra.protesto') or _('New')
        records = super().create(vals_list)
        for record in records:
            if record.letra_id:
                record.letra_id.write({
                    'state': 'protested',
                    'protest_date': record.date_protest,
                })
                record._create_debit_note()
        return records

    def _create_debit_note(self):
        for r in self:
            if r.gastos <= 0 or r.debit_note_id:
                continue
            company = r.letra_id.company_id or r.company_id or self.env.company
            journal = self.env['account.journal'].search(
                [('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': r.partner_id.id,
                'invoice_date': r.date_protest or fields.Date.today(),
                'ref': _('Gastos de Protesto - Letra %s') % r.letra_id.name,
                'invoice_line_ids': [(0, 0, {
                    'name': _('Gastos y Costas de Protesto Bancario - Letra %s') % r.letra_id.name,
                    'quantity': 1,
                    'price_unit': r.gastos,
                })],
            }
            if journal:
                move_vals['journal_id'] = journal.id
            debit_note = self.env['account.move'].sudo().create(move_vals)
            r.debit_note_id = debit_note.id
            r.letra_id.debit_note_id = debit_note.id


    def action_resolve(self):
        self.state = 'resolved'
        self.resolution_date = fields.Date.today()

