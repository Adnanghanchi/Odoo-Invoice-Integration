# -*- coding: utf-8 -*-
# from odoo import http


# class MyInvoiceEventListener(http.Controller):
#     @http.route('/my_invoice_event_listener/my_invoice_event_listener', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_invoice_event_listener/my_invoice_event_listener/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_invoice_event_listener.listing', {
#             'root': '/my_invoice_event_listener/my_invoice_event_listener',
#             'objects': http.request.env['my_invoice_event_listener.my_invoice_event_listener'].search([]),
#         })

#     @http.route('/my_invoice_event_listener/my_invoice_event_listener/objects/<model("my_invoice_event_listener.my_invoice_event_listener"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_invoice_event_listener.object', {
#             'object': obj
#         })

