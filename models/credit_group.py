from odoo import api, fields, models, _


class CreditGroup(models.Model):
    _name = 'l10n.pe.credit.group'
    _description = 'Grupo Empresarial para Líneas de Crédito'

    name = fields.Char(string='Nombre del Grupo', required=True)
    partner_ids = fields.One2many('res.partner', 'credit_group_id',
                                  string='Empresas del Grupo')
    partner_count = fields.Integer(string='Cant. Empresas',
                                   compute='_compute_partner_count')

    credit_limit = fields.Monetary(string='Línea de Crédito Asignada',
                                   required=True)
    credit_used = fields.Monetary(string='Crédito Utilizado',
                                  compute='_compute_credit_used')
    credit_available = fields.Monetary(string='Crédito Disponible',
                                       compute='_compute_credit_used')

    pending_orders_amount = fields.Monetary(
        string='Pedidos Pendientes',
        compute='_compute_credit_used')
    invoiced_amount = fields.Monetary(
        string='Facturado',
        compute='_compute_credit_used')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Compañía',
                                 default=lambda self: self.env.company)

    active = fields.Boolean(default=True)

    def _compute_partner_count(self):
        for r in self:
            r.partner_count = len(r.partner_ids)

    @api.depends('partner_ids', 'credit_limit')
    def _compute_credit_used(self):
        for r in self:
            partners = r.partner_ids
            # Facturas pendientes (no pagadas)
            invoices = self.env['account.move'].search([
                ('partner_id', 'in', partners.ids),
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('payment_state', 'not in', ('paid', 'reversed')),
                ('state', '=', 'posted'),
            ])
            invoiced_amount = sum(invoices.mapped('amount_residual'))

            # Pedidos pendientes de despacho (no facturados)
            orders = self.env['sale.order'].search([
                ('partner_id', 'in', partners.ids),
                ('state', 'in', ('sale', 'done')),
                ('invoice_status', '=', 'to invoice'),
            ])
            pending_orders_amount = sum(orders.mapped('amount_total'))

            # Letras emitidas pendientes
            letras = self.env['l10n.pe.letra'].search([
                ('partner_id', 'in', partners.ids),
                ('state', 'not in', ('cancelled', 'paid', 'protested')),
            ])
            letras_amount = sum(letras.mapped('amount_residual'))

            total_used = invoiced_amount + pending_orders_amount + letras_amount

            r.invoiced_amount = invoiced_amount
            r.pending_orders_amount = pending_orders_amount
            r.credit_used = total_used
            r.credit_available = r.credit_limit - total_used if r.credit_limit > 0 else 0

    def _check_blocked(self):
        self.ensure_one()
        partners = self.partner_ids
        protestadas = self.env['l10n.pe.letra'].search([
            ('partner_id', 'in', partners.ids),
            ('state', '=', 'protested'),
        ])
        return bool(protestadas.filtered(
            lambda l: any(p.state == 'pending' for p in l.protesto_ids)
        ))

    def _get_credit_available(self):
        self.ensure_one()
        self._compute_credit_used()
        return self.credit_available
