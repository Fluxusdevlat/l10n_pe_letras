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
    ], string='Estado', default='pending', tracking=True)

    resolution_date = fields.Date(string='Fecha de Regularización')
    resolution_type = fields.Selection([
        ('payment', 'Pago'),
        ('renewal', 'Renovación'),
        ('agreement', 'Acuerdo'),
        ('other', 'Otro'),
    ], string='Tipo de Regularización')

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
            letra = self.env['l10n.pe.letra'].browse(vals.get('letra_id'))
            letra.state = 'protested'
        return super().create(vals_list)

    def action_resolve(self):
        self.state = 'resolved'
        self.resolution_date = fields.Date.today()
