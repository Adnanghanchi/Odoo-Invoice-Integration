from odoo import http
from odoo.http import request

class CustomMailController(http.Controller):
    _inherit = 'mail.controller.main'

    @http.route('/my_invoice_event_listener/installation', type='json', auth='public')
    def handle_module_installation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'api.credentials.wizard',
            'views': [[False, 'form']],
            'target': 'new', 
        }
