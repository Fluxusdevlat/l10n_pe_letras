from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LetraRenovacionWizard(models.TransientModel):
    _name = 'l10n.pe.letra.renovacion.wizard'
    _description = 'Asistente de Renovación de Letra'

    letra_origin_id = fields.Many2one('l10n.pe.letra',
                                      string='Letra a Renovar',
                                      required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente',
                                 required=True)
    date_emission = fields.Date(string='Fecha de Emisión',
                                default=fields.Date.context_today,
                                required=True)
    days_term = fields.Selection([('30', '30 Días (Obligatorio Banco)')],
                                 string='Plazo Renovación', default='30',
                                 readonly=True, required=True)
    date_due = fields.Date(string='Nueva Fecha de Vencimiento (30 días)',
                           compute='_compute_date_due', store=True, readonly=False)
    bank_id = fields.Many2one('res.bank', string='Banco')

    @api.depends('date_emission', 'days_term')
    def _compute_date_due(self):
        from datetime import timedelta
        for r in self:
            if r.date_emission:
                r.date_due = r.date_emission + timedelta(days=30)


    amount_origin = fields.Monetary(string='Monto Original',
                                    related='letra_origin_id.amount_residual')
    intereses = fields.Monetary(string='Intereses', default=0.0)
    gastos = fields.Monetary(string='Gastos', default=0.0)
    amount_new = fields.Monetary(string='Nuevo Monto', required=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)

    reason = fields.Text(string='Motivo de Renovación')

    @api.onchange('amount_origin', 'intereses', 'gastos')
    def _onchange_calc_new_amount(self):
        for r in self:
            r.amount_new = r.amount_origin + r.intereses + r.gastos

    def action_renew(self):
        self.ensure_one()

        letra_new = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner_id.id,
            'bank_id': self.bank_id.id,
            'amount_total': self.amount_new,
            'date_emission': self.date_emission,
            'date_due': self.date_due,
            'tipo': 'canje',
            'renovacion_origin_id': self.letra_origin_id.id,
            'is_renovacion': True,
        })

        self.env['l10n.pe.letra.renovacion'].create({
            'letra_origin_id': self.letra_origin_id.id,
            'letra_new_id': letra_new.id,
            'date': fields.Date.today(),
            'amount_new': self.amount_new,
            'intereses': self.intereses,
            'gastos': self.gastos,
            'reason': self.reason,
        })

        self.letra_origin_id.state = 'renewed'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra',
            'view_mode': 'form',
            'res_id': letra_new.id,
        }
