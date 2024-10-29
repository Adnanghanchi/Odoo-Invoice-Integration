#1.odoo\addons\my_invoice_event_listener\wizards\sadad_api_credentials.py 
from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ApiCredentialsWizard(models.Model):
    _name = 'api.credentials.wizard'
    _description = 'Create API Credentials'

    sadad_id = fields.Char('Sadad ID', required=True)
    secret_key = fields.Char('Secret Key', required=True)
    domain = fields.Char('Domain', required=True)

    

    def action_create_api_credentials(self):
        _logger.info("Button clicked for creating API credentials")

        # Check if all required fields are filled
        if not (self.sadad_id and self.secret_key and self.domain):
            raise exceptions.ValidationError(("Please fill in all required fields: Sadad ID, Secret Key, and Domain"))
        
        # Search for existing record
        existing_record = self.env['api.credentials.wizard'].search([
            ('sadad_id', '=', self.sadad_id),
            ('secret_key', '=', self.secret_key),
            ('domain', '=', self.domain)
        ])

        if existing_record:
            # Update existing record
            existing_record.write({
                'sadad_id': self.sadad_id,
                'secret_key': self.secret_key,
                'domain': self.domain
            })
            
            _logger.info("API credentials updated successfully")
        else:
            # Create new record
            new_record = self.env['api.credentials.wizard'].create({
                'sadad_id': self.sadad_id,
                'secret_key': self.secret_key,
                'domain': self.domain
            })

            _logger.info(f"API credentials: {new_record}")
            _logger.info("API credentials created successfully")
        
        # Display a success message
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Success'),
                'message': ('API credentials have been successfully updated/created and stored in the database.'),
                'sticky': False,
            },
        }

        # Close the window after successful creation/update
        close_window = {'type': 'ir.actions.act_window_close'}

        # Return a list of actions to execute
        return [notification, close_window]


    








































# from odoo import models, fields, api, exceptions
# import logging

# _logger = logging.getLogger(__name__)

# class ApiCredentialsWizard(models.Model):
#     _name = 'api.credentials.wizard'
#     _description = 'Create Api Credentials'

#     sadad_id = fields.Char('Sadad ID', required=True)
#     secret_key = fields.Char('Secret Key', required=True)
#     domain = fields.Char('Domain', required=True)

#     # def apply_configuration(self):
#     #      # Retrieve the configuration values entered by the user
#     #     sadad_id = self.sadad_id
#     #     secret_key = self.secret_key
#     #     domain = self.domain

#     #     # Apply configuration logic here
#     #     # You can store the values in the database or use them directly in your module
#     #     self.env['ir.config_parameter'].sudo().set_param('sadad.sadad_id', sadad_id)
#     #     self.env['ir.config_parameter'].sudo().set_param('sadad.secret_key', secret_key)
#     #     self.env['ir.config_parameter'].sudo().set_param('sadad.domain', domain)

#     def action_create_api_credentials(self):
        
#         print("Buttton IS clicked")
#         _logger.info("Buttton IS clicked")

#         #check if all reuired fields are filled
#         if not (self.sadad_id and self.secret_key and self.domain):
#             raise exceptions.ValidationError("Please fill in all required fields: Sadad ID, Secret Key, and Domain")
        
#         #Store the API Credentials in the database
#         credentials = self.env['api.credentials.wizard'].create({
#             'sadad_id': self.sadad_id,
#             'secret_key': self.secret_key,
#             'domain': self.domain
#         })

#         _logger.info(f"sadad_id{credentials.sadad_id}")
#         _logger.info(f"secret_key{credentials.secret_key}")
#         _logger.info(f"domain{credentials.domain}")


#         # # Log a message indicating successful credential creation
#         # self.env['ir.logging'].sudo().create({
#         #     'name': 'API Credentials Created',
#         #     'type': 'notification', 
#         #     'message': 'API credentials have been successfully created and stored in the database.'
#         # })

#         # Display a success message
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Success',
#                 'message': 'API credentials have been successfully created and stored in the database.',
#                 'sticky': False,
#             },
#         }
    
#     # @api.model
#     # def init(self):
#     # # Check if any records exist in api.credentials.wizard
#     #     credentials = self.env['api.credentials.wizard'].search([], limit=1)
       
#     #     if not (credentials.sadad_id and credentials.secret_key and credentials.domain):
#     #         _logger.info("aaaaaaa")
#     #         # Open the wizard action
#     #         action = self.env.ref('my_invoice_event_listener.action_create_api_credentials')
#     #         _logger.info("BBBBBBBBBBBBBBBBBBBBBBBBBB")

#     #         return action.read()[0]
        
#     #     _logger.info("CCCCCCCCCCCCCCCCCCCCCCC")
#             # if action:
#             #     #if the action is found, read its data
#             #     # action_data = action.read()[0]
#             #     # return action_data

#             #     # return {
#             #     # 'type': 'ir.actions.act_window',
#             #     # 'res_model': action.res_model,
#             #     # 'views': [[False, 'form']],
#             #     # 'target': 'new',
#             #     # }
#             # else:
#             #      # Log a warning if the action is not found
#             #     _logger.warning("Action 'action_api_credentials' not found.")

#     # @api.model
#     # def init(self):
#     #       # Check if any records exist in api.credentials.wizard
#     #     credentials = self.env['api.credentials.wizard'].search([], limit=1)
#     #     if not credentials:
#     #         # Open the wizard action if no records exist
#     #         action = self.env.ref('my_invoice_event_listener.action_create_api_credentials')
#     #         if action:
#     #             return action.read()[0]
#     #         else:
#     #             _logger.warning("Action 'action_create_api_credentials' not found.") 
#     #     return None
