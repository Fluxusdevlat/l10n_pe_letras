from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    letra_line_ids = fields.One2many('l10n.pe.letra.line', 'move_id',
                                     string='Letras Asociadas')
    letra_count = fields.Integer(string='Cant. Letras',
                                 compute='_compute_letra_count')
    letra_amount_total = fields.Monetary(
        string='Monto en Letras',
        compute='_compute_letra_amount')

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

    def _compute_letra_count(self):
        for r in self:
            r.letra_count = len(r.letra_line_ids)

    def _compute_letra_amount(self):
        for r in self:
            r.letra_amount_total = sum(r.letra_line_ids.mapped('amount'))

    @api.depends('amount_residual', 'letra_amount_total')
    def _compute_letra_state(self):
        for r in self:
            if r.letra_amount_total == 0:
                r.letra_state = 'without'
            elif r.letra_amount_total >= r.amount_total:
                r.letra_state = 'total'
            else:
                r.letra_state = 'partial'
