from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    letras_global_credit_limit = fields.Monetary(
        string='Techo Agregado de Líneas de Crédito',
        currency_field='currency_id',
        help='Monto máximo que puede sumar el total de líneas de crédito '
             'otorgadas a todos los grupos empresariales de la compañía. '
             'Use 0 para no aplicar límite.')
