from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GenerateLetrasWizard(models.TransientModel):
    _name = 'l10n.pe.letra.generate.wizard'
    _description = 'Generar Letras desde Facturas'

    invoice_ids = fields.Many2many('account.move', string='Facturas',
                                   domain=[('move_type', '=', 'out_invoice'),
                                           ('payment_state', 'not in', ('paid', 'reversed'))],
                                   required=True)
    partner_id = fields.Many2one(related='invoice_ids.partner_id',
                                 string='Cliente', readonly=True)

    date_emission = fields.Date(string='Fecha de Emisión',
                                default=fields.Date.context_today,
                                required=True)
    date_due = fields.Date(string='Fecha de Vencimiento',
                           required=True)

    bank_id = fields.Many2one('res.bank', string='Banco')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(string='Importe Total',
                                   currency_field='currency_id',
                                   compute='_compute_amount_total')

    generate_option = fields.Selection([
        ('one_per_invoice', 'Una Letra por Factura'),
        ('single', 'Una Letra por todas las Facturas'),
    ], string='Opción de Generación', default='one_per_invoice',
        required=True)

    @api.depends('invoice_ids', 'invoice_ids.amount_residual')
    def _compute_amount_total(self):
        for r in self:
            r.amount_total = sum(r.invoice_ids.mapped('amount_residual'))

    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        if self.invoice_ids:
            partners = self.invoice_ids.mapped('partner_id')
            if len(partners) > 1:
                return {'warning': {
                    'title': 'Advertencia',
                    'message': 'Las facturas seleccionadas pertenecen a diferentes clientes. '
                               'Se usará la opción "Una Letra por Factura".',
                }}

    def action_generate(self):
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_('Debe seleccionar al menos una factura'))

        Letra = self.env['l10n.pe.letra']
        LetraLine = self.env['l10n.pe.letra.line']

        if self.generate_option == 'single':
            return self._generate_single_letra()
        else:
            return self._generate_one_per_invoice()

    def _generate_single_letra(self):
        invoices = self.invoice_ids
        LetraLine = self.env['l10n.pe.letra.line']
        partner = invoices.mapped('partner_id')
        if len(partner) > 1:
            raise UserError(_(
                'No se puede generar una sola letra para facturas '
                'de diferentes clientes'))

        letra = self.env['l10n.pe.letra'].create({
            'partner_id': partner.id,
            'bank_id': self.bank_id.id,
            'amount_total': self.amount_total,
            'date_emission': self.date_emission,
            'date_due': self.date_due,
            'tipo': 'emission',
        })

        for inv in invoices:
            LetraLine.create({
                'letra_id': letra.id,
                'move_id': inv.id,
                'amount': inv.amount_residual,
            })

        return self._open_letra(letra)

    def _generate_one_per_invoice(self):
        invoices = self.invoice_ids
        letras = self.env['l10n.pe.letra']
        LetraLine = self.env['l10n.pe.letra.line']

        for inv in invoices:
            letra = self.env['l10n.pe.letra'].create({
                'partner_id': inv.partner_id.id,
                'bank_id': self.bank_id.id,
                'amount_total': inv.amount_residual,
                'date_emission': self.date_emission,
                'date_due': self.date_due,
                'tipo': 'emission',
            })
            LetraLine.create({
                'letra_id': letra.id,
                'move_id': inv.id,
                'amount': inv.amount_residual,
            })
            letras |= letra

        return self._open_letras(letras)

    def _open_letra(self, letra):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra',
            'view_mode': 'form',
            'res_id': letra.id,
        }

    def _open_letras(self, letras):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.pe.letra',
            'view_mode': 'list,form',
            'domain': [('id', 'in', letras.ids)],
        }
