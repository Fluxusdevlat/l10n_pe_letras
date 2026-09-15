{
    'name': 'Letras de Cambio - Perú',
    'version': '19.0.1.31.0',





    'summary': 'Gestión de Letras de Cambio para empresas peruanas',
    'description': """
Módulo para la gestión completa de Letras de Cambio:
- Registro y administración de letras
- Generación automática desde facturas
- Asociación flexible facturas <> letras
- Control de estados (pendiente, enviada, firmada, en banco, protestada, cancelada, renovada, pagada)
- Impresión de letras formato oficial
- Planillas para envío a bancos
- Protestos y renovaciones
- Bloqueo comercial por letras protestadas
- Reportes de cartera financiera
    """,
    'category': 'Accounting/Localizations/Reporting',
    'author': 'Tu Empresa',
    'website': 'https://tusitio.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'sale',
        'l10n_pe',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/letra_sequence.xml',
        'views/letra_protesto_views.xml',
        'views/letra_renovacion_views.xml',
        'views/letra_planilla_views.xml',
        'views/letra_views.xml',
        'views/credit_group_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
        'wizards/generar_letras_wizard_views.xml',
        'wizards/renovacion_wizard_views.xml',
        'wizards/enviar_letras_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'reports/letra_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {},
}
