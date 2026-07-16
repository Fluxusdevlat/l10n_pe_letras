from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_group_id = fields.Many2one('l10n.pe.credit.group',
                                      string='Grupo Empresarial')

    letra_ids = fields.One2many('l10n.pe.letra', 'partner_id',
                                string='Letras')
    letra_count = fields.Integer(string='Cant. Letras',
                                 compute='_compute_letra_count')

    letra_protestada_count = fields.Integer(
        string='Letras Protestadas Pendientes',
        compute='_compute_letra_protestada')

    has_letras_protestadas = fields.Boolean(
        string='Tiene Letras Protestadas',
        compute='_compute_letra_protestada')

    commercial_blocked = fields.Boolean(
        string='Bloqueado Comercialmente',
        compute='_compute_commercial_blocked',
        store=True)
    commercial_block_reason = fields.Char(
        string='Motivo de Bloqueo',
        compute='_compute_commercial_blocked',
        store=True)

    def _compute_letra_count(self):
        for r in self:
            r.letra_count = self.env['l10n.pe.letra'].search_count([
                ('partner_id', '=', r.id),
                ('state', 'not in', ('cancelled', 'paid')),
            ])

    def _compute_letra_protestada(self):
        for r in self:
            protestadas = self.env['l10n.pe.letra'].search([
                ('partner_id', '=', r.id),
                ('state', '=', 'protested'),
            ])
            pendientes = protestadas.filtered(
                lambda l: any(p.state == 'pending' for p in l.protesto_ids)
            )
            r.letra_protestada_count = len(pendientes)
            r.has_letras_protestadas = bool(pendientes)

    @api.depends('has_letras_protestadas', 'credit_group_id')
    def _compute_commercial_blocked(self):
        for r in self:
            blocked = False
            reason = ''
            if r.has_letras_protestadas:
                blocked = True
                reason = 'Tiene letras protestadas pendientes de regularización'
            if not blocked and r.credit_group_id:
                group_blocked = r.credit_group_id._check_blocked()
                if group_blocked:
                    blocked = True
                    reason = 'El grupo empresarial tiene letras protestadas'
            r.commercial_blocked = blocked
            r.commercial_block_reason = reason
