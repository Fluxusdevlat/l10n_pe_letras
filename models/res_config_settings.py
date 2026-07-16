from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    letras_email_to = fields.Char(
        string='Email para envío de Letras',
        default='',
        config_parameter='l10n_pe_letras.email_to',
        help='Correo destino al que se enviarán las letras desde el wizard "Enviar Letras por Email"')
