from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    letras_currency_id = fields.Many2one('res.currency',
                                         related='company_id.currency_id',
                                         string='Moneda')

    letras_email_to = fields.Char(
        string='Email para envío de Letras',
        default='',
        config_parameter='l10n_pe_letras.email_to',
        help='Correo destino al que se enviarán las letras desde el wizard "Enviar Letras por Email"')

    letras_global_credit_limit = fields.Monetary(
        string='Techo Agregado de Líneas de Crédito',
        related='company_id.letras_global_credit_limit',
        readonly=False,
        currency_field='letras_currency_id',
        help='Monto máximo que puede sumar el total de líneas de crédito '
             'otorgadas a los grupos empresariales. 0 = sin límite.')
