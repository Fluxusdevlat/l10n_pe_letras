from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_protest_debit_note = fields.Boolean(
        string='Es Nota de Débito de Protesto', copy=False,
        help='Marca interna: la nota de débito de gastos de protesto puede '
             'validarse aunque el cliente esté bloqueado.')

    letra_line_ids = fields.One2many('l10n.pe.letra.line', 'move_id',
                                     string='Letras Asociadas')
    letra_count = fields.Integer(string='Cant. Letras',
                                 compute='_compute_letra_count')
    letra_amount_total = fields.Monetary(
        string='Monto en Letras',
        compute='_compute_letra_amount',
        store=True)

    letra_state = fields.Selection([
        ('without', 'Sin Letra'),
        ('partial', 'Parcialmente en Letras'),
        ('total', 'Totalmente en Letras'),
    ], string='Estado Letras', compute='_compute_letra_state', store=True)

    is_negociable_cavali = fields.Boolean(string='Factura Negociable CAVALI')
    cavali_state = fields.Selection([
        ('pending', 'Pendiente'),
        ('negotiated', 'Negociada'),
        ('paid', 'Cancelada'),
    ], string='Estado CAVALI')
    cavali_date = fields.Date(string='Fecha Negociación CAVALI')

    factoring_state = fields.Selection([
        ('pending', 'Pendiente'),
        ('ceded', 'Cedida'),
        ('paid', 'Cancelada'),
    ], string='Estado Factoring')
    factoring_entity_id = fields.Many2one('res.partner',
                                          string='Entidad Factor',
                                          domain=[('is_company', '=', True)])
    factoring_date = fields.Date(string='Fecha Cesión')

    @api.depends('letra_line_ids', 'letra_line_ids.amount',
                 'letra_line_ids.letra_id.state')
    def _compute_letra_count(self):
        for r in self:
            lines = r.letra_line_ids.filtered(
                lambda l: l.letra_id.state != 'cancelled')
            r.letra_count = len(lines)

    @api.depends('letra_line_ids', 'letra_line_ids.amount',
                 'letra_line_ids.letra_id.state')
    def _compute_letra_amount(self):
        for r in self:
            lines = r.letra_line_ids.filtered(
                lambda l: l.letra_id.state != 'cancelled')
            r.letra_amount_total = sum(lines.mapped('amount'))

    @api.depends('amount_residual', 'letra_amount_total')
    def _compute_letra_state(self):
        for r in self:
            available = r.amount_residual - r.letra_amount_total
            if r.letra_amount_total <= 0:
                r.letra_state = 'without'
            elif available <= 0.005:
                r.letra_state = 'total'
            else:
                r.letra_state = 'partial'

    def action_post(self):
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund') \
                    and not move.is_protest_debit_note \
                    and move.partner_id.commercial_blocked:
                raise UserError(_(
                    'No se puede validar la factura. El cliente %s está '
                    'bloqueado comercialmente. Motivo: %s'
                ) % (move.partner_id.name,
                     move.partner_id.commercial_block_reason))
        return super().action_post()
