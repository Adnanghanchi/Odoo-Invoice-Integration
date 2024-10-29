{
    'name': 'Odoo Sadad QA Invoice Integration',
    'version': '1.0',
    'price': 50.00,
    'currency': 'USD',
    'author': "Sufalam Technologies",
    'website':'https://www.sufalamtech.com',
    'license': 'AGPL-3',
    'summary': 'Listens to Invoice Creation Events',
    'sequence': 10,
    'description': """<p>Listens to events when an invoice is created and performs actions.</p>""",
    'category': 'Accounting',
    'depends': ['base', 'account'],
    'images': ['images/SADAD.png'],
    'data': [
        
        'security/ir.model.access.csv', 
        'wizards/sadad_api_credentials_view.xml',
        'views/todo_open_wizard.xml',
        'views/sadad_api_credentials_menu.xml',
        'views/account_invoice_tree_inherit.xml'
        ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
