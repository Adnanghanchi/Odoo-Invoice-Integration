# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class my_invoice_event_listener(models.Model):
#     _name = 'my_invoice_event_listener.my_invoice_event_listener'
#     _description = 'my_invoice_event_listener.my_invoice_event_listener'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

