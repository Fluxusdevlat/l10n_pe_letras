from odoo import api, fields, models, _


class LetraRenovacion(models.Model):
    _name = 'l10n.pe.letra.renovacion'
    _description = 'Renovación de Letra'
    _order = 'date desc, id desc'

    name = fields.Char(string='N° Renovación', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    letra_origin_id = fields.Many2one('l10n.pe.letra',
                                      string='Letra Origen',
                                      required=True)
    letra_new_id = fields.Many2one('l10n.pe.letra',
                                   string='Nueva Letra',
                                   required=True)
    partner_id = fields.Many2one(related='letra_origin_id.partner_id',
                                 string='Cliente', store=True)
    date = fields.Date(string='Fecha de Renovación',
                       default=fields.Date.context_today,
                       required=True)
    amount_origin = fields.Monetary(string='Monto Original',
                                    related='letra_origin_id.amount_residual')
    amount_new = fields.Monetary(string='Nuevo Monto', required=True)
    difference = fields.Monetary(string='Diferencia',
                                 compute='_compute_difference', store=True)
    intereses = fields.Monetary(string='Intereses', default=0.0)
    gastos = fields.Monetary(string='Gastos', default=0.0)

    currency_id = fields.Many2one('res.currency',
                                  related='letra_origin_id.currency_id')
    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company)

    reason = fields.Text(string='Motivo de Renovación')

    @api.depends('amount_origin', 'amount_new', 'intereses', 'gastos')
    def _compute_difference(self):
        for r in self:
            r.difference = r.amount_new - r.amount_origin + r.intereses + r.gastos

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'l10n.pe.letra.renovacion') or _('New')
        return super().create(vals_list)
