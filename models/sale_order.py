from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_has_letras_protestadas = fields.Boolean(
        related='partner_id.has_letras_protestadas',
        string='Cliente con Letras Protestadas')
    partner_commercial_blocked = fields.Boolean(
        related='partner_id.commercial_blocked',
        string='Cliente Bloqueado')
    partner_credit_near_limit = fields.Boolean(
        related='partner_id.credit_near_limit',
        string='Cerca del Límite de Crédito')

    def action_confirm(self):
        for order in self:
            partner = order.partner_id
            if partner.commercial_blocked:
                raise UserError(_(
                    'No se puede confirmar el pedido. '
                    'El cliente %s está bloqueado comercialmente. '
                    'Motivo: %s'
                ) % (partner.name, partner.commercial_block_reason))

            if partner.credit_group_id:
                credit_available = partner.credit_group_id._get_credit_available()
                if credit_available is not None and credit_available < order.amount_total:
                    raise UserError(_(
                        'No se puede confirmar el pedido. '
                        'El cliente %s excede la línea de crédito disponible '
                        'del grupo empresarial %s. '
                        'Crédito disponible: %s'
                    ) % (partner.name, partner.credit_group_id.name, credit_available))

        return super().action_confirm()
