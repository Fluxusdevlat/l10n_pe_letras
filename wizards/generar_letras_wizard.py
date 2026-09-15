from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class GenerateLetrasWizard(models.TransientModel):
    _name = 'l10n.pe.letra.generate.wizard'
    _description = 'Generar Letras desde Facturas'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'invoice_ids' in fields_list and not res.get('invoice_ids'):
            active_model = self.env.context.get('active_model')
            active_ids = self.env.context.get('active_ids') or (
                [self.env.context.get('active_id')] if self.env.context.get('active_id') else []
            )
            if active_model == 'account.move' and active_ids:
                invoices = self.env['account.move'].browse(active_ids).filtered(
                    lambda m: m.move_type == 'out_invoice' and m.payment_state not in ('paid', 'reversed')
                )
                if invoices:
                    res['invoice_ids'] = [(6, 0, invoices.ids)]
            elif self.env.context.get('default_partner_id'):
                partner_id = self.env.context.get('default_partner_id')
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', partner_id),
                    ('move_type', '=', 'out_invoice'),
                    ('payment_state', 'not in', ('paid', 'reversed'))
                ])
                if invoices:
                    res['invoice_ids'] = [(6, 0, invoices.ids)]
        return res

    invoice_ids = fields.Many2many('account.move', string='Facturas',
                                   domain=[('move_type', '=', 'out_invoice'),
                                           ('payment_state', 'not in', ('paid', 'reversed'))],
                                   required=True)
    partner_id = fields.Many2one(related='invoice_ids.partner_id',
                                 string='Cliente', readonly=True)

    date_emission = fields.Date(string='Fecha de Emisión',
                                default=fields.Date.context_today,
                                required=True)
    date_due = fields.Date(string='Fecha de Vencimiento General')

    bank_id = fields.Many2one('res.bank', string='Banco')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(string='Importe Total',
                                   currency_field='currency_id',
                                   compute='_compute_amount_total')

    generate_option = fields.Selection([
        ('one_per_invoice', 'Una Letra por Factura'),
        ('single', 'Una Letra por todas las Facturas'),
        ('multiple_letras', 'Dividir una Factura en Varias Letras (Cuotas)'),
    ], string='Opción de Generación', default='one_per_invoice',
        required=True)

    num_letras = fields.Integer(string='Cantidad de Letras (Cuotas)', default=3)
    days_interval = fields.Integer(string='Intervalo (Días entre Vencimientos)', default=30)

    line_ids = fields.One2many('l10n.pe.letra.generate.wizard.line', 'wizard_id',
                               string='Vista Previa de Letras / Cuotas')

    @api.depends('invoice_ids', 'invoice_ids.amount_residual')
    def _compute_amount_total(self):
        for r in self:
            r.amount_total = sum(r.invoice_ids.mapped('amount_residual'))

    @api.onchange('invoice_ids', 'date_emission')
    def _onchange_invoices_or_date(self):
        if self.invoice_ids:
            partners = self.invoice_ids.mapped('partner_id')
            if len(partners) > 1:
                return {'warning': {
                    'title': 'Advertencia',
                    'message': 'Las facturas seleccionadas pertenecen a diferentes clientes. '
                               'Se usará la opción "Una Letra por Factura".',
                }}
        if self.date_emission and not self.date_due:
            partners = self.invoice_ids.mapped('partner_id') if self.invoice_ids else False
            days = 30
            if partners and partners[0].letra_days_term:
                try:
                    days = int(partners[0].letra_days_term)
                except ValueError:
                    days = 30
            self.date_due = self.date_emission + timedelta(days=days)

    @api.onchange('generate_option', 'invoice_ids', 'num_letras', 'days_interval', 'date_emission', 'date_due')
    def _onchange_recompute_lines(self):
        lines = [(5, 0, 0)]
        if not self.invoice_ids or not self.date_emission:
            self.line_ids = lines
            return

        if self.generate_option == 'multiple_letras':
            if len(self.invoice_ids) == 1 and self.num_letras >= 2:
                inv = self.invoice_ids[0]
                total_amount = inv.amount_residual
                num = self.num_letras
                base_amount = round(total_amount / num, 2)
                remainder = round(total_amount - (base_amount * num), 2)

                first_due = self.date_due
                for i in range(1, num + 1):
                    letra_amount = base_amount + (remainder if i == num else 0.0)
                    if first_due:
                        due_date = first_due + timedelta(days=self.days_interval * (i - 1))
                    else:
                        days = self.days_interval * i
                        due_date = self.date_emission + timedelta(days=days)

                    lines.append((0, 0, {
                        'sequence': i,
                        'name': _('Cuota %s de %s - Factura %s') % (i, num, inv.name),
                        'date_due': due_date,
                        'amount': letra_amount,
                        'move_id': inv.id,
                    }))
        elif self.generate_option == 'single':
            partner = self.invoice_ids.mapped('partner_id')
            if len(partner) == 1:
                due_date = self.date_due
                if not due_date:
                    days = int(partner.letra_days_term or 30) if partner and partner.letra_days_term else 30
                    due_date = self.date_emission + timedelta(days=days)

                inv_names = ", ".join(self.invoice_ids.mapped('name'))
                lines.append((0, 0, {
                    'sequence': 1,
                    'name': _('Letra Única - Facturas: %s') % inv_names,
                    'date_due': due_date,
                    'amount': self.amount_total,
                }))
        elif self.generate_option == 'one_per_invoice':
            for i, inv in enumerate(self.invoice_ids, 1):
                due_date = self.date_due or inv.invoice_date_due
                if not due_date:
                    days = int(inv.partner_id.letra_days_term or 30) if inv.partner_id.letra_days_term else 30
                    due_date = self.date_emission + timedelta(days=days)
                lines.append((0, 0, {
                    'sequence': i,
                    'name': _('Letra por Factura %s') % inv.name,
                    'date_due': due_date,
                    'amount': inv.amount_residual,
                    'move_id': inv.id,
                }))

        self.line_ids = lines

    def action_generate(self):
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_('Debe seleccionar al menos una factura'))

        if self.generate_option == 'single':
            return self._generate_single_letra()
        elif self.generate_option == 'multiple_letras':
            return self._generate_multiple_letras_from_invoice()
        else:
            return self._generate_one_per_invoice()

    def _generate_multiple_letras_from_invoice(self):
        if len(self.invoice_ids) != 1:
            raise UserError(_('Para dividir en varias letras, seleccione exactamente una factura.'))
        if self.num_letras < 2:
            raise UserError(_('La cantidad de letras debe ser al menos 2.'))

        inv = self.invoice_ids[0]
        letras = self.env['l10n.pe.letra']
        LetraLine = self.env['l10n.pe.letra.line']

        if self.line_ids:
            for line in self.line_ids:
                days = (line.date_due - self.date_emission).days if line.date_due and self.date_emission else 30
                term_str = str(days) if str(days) in ('30', '60', '90', '120', '150') else '30'

                letra = self.env['l10n.pe.letra'].create({
                    'partner_id': inv.partner_id.id,
                    'bank_id': self.bank_id.id,
                    'amount_total': line.amount,
                    'date_emission': self.date_emission,
                    'days_term': term_str,
                    'date_due': line.date_due,
                    'tipo': 'emission',
                    'notes': line.name,
                })
                LetraLine.create({
                    'letra_id': letra.id,
                    'move_id': inv.id,
                    'amount': line.amount,
                })
                letras |= letra
        else:
            total_amount = inv.amount_residual
            num = self.num_letras
            base_amount = round(total_amount / num, 2)
            remainder = round(total_amount - (base_amount * num), 2)

            for i in range(1, num + 1):
                letra_amount = base_amount + (remainder if i == num else 0.0)
                days = self.days_interval * i
                due_date = self.date_emission + timedelta(days=days)
                term_str = str(days) if str(days) in ('30', '60', '90', '120', '150') else '30'

                letra = self.env['l10n.pe.letra'].create({
                    'partner_id': inv.partner_id.id,
                    'bank_id': self.bank_id.id,
                    'amount_total': letra_amount,
                    'date_emission': self.date_emission,
                    'days_term': term_str,
                    'date_due': due_date,
                    'tipo': 'emission',
                    'notes': _('Cuota %s de %s - Factura %s') % (i, num, inv.name),
                })
                LetraLine.create({
                    'letra_id': letra.id,
                    'move_id': inv.id,
                    'amount': letra_amount,
                })
                letras |= letra

        return self._open_letras(letras)

    def _generate_single_letra(self):
        invoices = self.invoice_ids
        LetraLine = self.env['l10n.pe.letra.line']
        partner = invoices.mapped('partner_id')
        if len(partner) > 1:
            raise UserError(_(
                'No se puede generar una sola letra para facturas '
                'de diferentes clientes'))

        due_date = self.date_due
        if not due_date and self.line_ids:
            due_date = self.line_ids[0].date_due
        if not due_date:
            days = int(partner.letra_days_term or 30) if partner and partner.letra_days_term else 30
            due_date = self.date_emission + timedelta(days=days)

        letra = self.env['l10n.pe.letra'].create({
            'partner_id': partner.id,
            'bank_id': self.bank_id.id,
            'amount_total': self.amount_total,
            'date_emission': self.date_emission,
            'date_due': due_date,
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

        if self.line_ids:
            for line in self.line_ids:
                inv = line.move_id or (invoices[0] if len(invoices) == 1 else False)
                if not inv:
                    continue
                due_date = line.date_due or self.date_due or inv.invoice_date_due
                if not due_date:
                    days = int(inv.partner_id.letra_days_term or 30) if inv.partner_id.letra_days_term else 30
                    due_date = self.date_emission + timedelta(days=days)

                letra = self.env['l10n.pe.letra'].create({
                    'partner_id': inv.partner_id.id,
                    'bank_id': self.bank_id.id,
                    'amount_total': line.amount,
                    'date_emission': self.date_emission,
                    'date_due': due_date,
                    'tipo': 'emission',
                })
                LetraLine.create({
                    'letra_id': letra.id,
                    'move_id': inv.id,
                    'amount': line.amount,
                })
                letras |= letra
        else:
            for inv in invoices:
                due_date = self.date_due or inv.invoice_date_due
                if not due_date:
                    days = int(inv.partner_id.letra_days_term or 30) if inv.partner_id.letra_days_term else 30
                    due_date = self.date_emission + timedelta(days=days)

                letra = self.env['l10n.pe.letra'].create({
                    'partner_id': inv.partner_id.id,
                    'bank_id': self.bank_id.id,
                    'amount_total': inv.amount_residual,
                    'date_emission': self.date_emission,
                    'date_due': due_date,
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


class GenerateLetrasWizardLine(models.TransientModel):
    _name = 'l10n.pe.letra.generate.wizard.line'
    _description = 'Detalle de Vista Previa de Letras'

    wizard_id = fields.Many2one('l10n.pe.letra.generate.wizard', ondelete='cascade')
    sequence = fields.Integer(string='N° Cuota', default=1)
    name = fields.Char(string='Concepto / Ref')
    date_due = fields.Date(string='Fecha de Vencimiento', required=True)
    amount = fields.Monetary(string='Monto de Cuota', required=True)
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')
    move_id = fields.Many2one('account.move', string='Factura')
