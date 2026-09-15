from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestLetraBasico(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Cliente Test Letras SAC',
            'is_company': True,
        })

    def test_secuencia_y_estado_inicial(self):
        letra = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner.id,
            'amount_total': 100.0,
        })
        self.assertNotEqual(letra.name, 'New')
        self.assertEqual(letra.state, 'draft')

    def test_vencimiento_por_plazo(self):
        letra = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner.id,
            'amount_total': 100.0,
            'date_emission': '2026-01-01',
            'days_term': '60',
        })
        self.assertEqual(str(letra.date_due), '2026-03-02')

    def test_firma_requiere_documento(self):
        letra = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner.id,
            'amount_total': 50.0,
        })
        letra.state = 'sent'
        with self.assertRaises(UserError):
            letra.action_signed()

    def test_cabal_no_requiere_documento(self):
        letra = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner.id,
            'amount_total': 50.0,
            'instrument_type': 'cabal',
        })
        letra.state = 'sent'
        letra.action_signed()
        self.assertEqual(letra.state, 'signed')

    def test_pago_deja_saldo_en_cero(self):
        letra = self.env['l10n.pe.letra'].create({
            'partner_id': self.partner.id,
            'amount_total': 200.0,
        })
        letra.action_paid()
        self.assertEqual(letra.state, 'paid')
        self.assertEqual(letra.amount_paid, 200.0)
        self.assertEqual(letra.amount_residual, 0.0)
