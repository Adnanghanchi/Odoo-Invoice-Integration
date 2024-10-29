#server\odoo\addons\my_invoice_event_listener\models\event_listener.py
from odoo import models, api, exceptions, fields
import logging
import requests

_logger = logging.getLogger(__name__)

class SadadApiResponse(models.Model):
    _name = 'sadad.api.response'
    _description = 'SADAD API RESPONSE'

    invoice_number = fields.Char(string='Invoice Number')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    response_date = fields.Datetime(string='Response Date', default=fields.Datetime.now)
    sadad_invoice_id = fields.Integer(string='Sadad Invoice Id')
    count = fields.Integer(string='Count')  # New field for storing the count information

class AccountMove(models.Model):
    _inherit = 'account.move'

    sadad_response_id = fields.Many2one('sadad.api.response', string='SADAD API Response', compute='_compute_sadad_response_id')
    invoice_no = fields.Char(related='sadad_response_id.invoice_number', string='SADAD Invoice No.', store=True)

    def _compute_sadad_response_id(self):
  
        for record in self:
    #         sadad_response = self.env['sadad.api.response'].search([('invoice_id', '=', record.id)], limit=1)
    #         record.sadad_response_id = sadad_response# def _compute_sadad_response_id(self):
    # #     for record in self:
            try:
                sadad_response = self.env['sadad.api.response'].search([('invoice_id', '=', record.id)], limit=1)
                if sadad_response:
                    record.sadad_response_id = sadad_response
                    record.invoice_no = sadad_response.invoice_number
                    _logger.info("invoice_no")
                else:
                    record.sadad_response_id = ")"
                    record.invoice_no = ")"
                    _logger.info("error invoice_no")
            except Exception as e:
                _logger.error(f"Error computing sadad_response_id for record ID {record.id}: {e}")
                record.sadad_response_id = False
                record.invoice_no = False


class InvoiceEventListener(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    @api.model
    def _check_company_currency(self):
        """
        Check if the company's currency is set to QAR during module installation.
        """
        message = "\033[1mPlease set the company's currency to Qatari Riyal (QAR) to use this module.\033[0m"
        message1 = "You can change the currency by navigating to:"
        path = "Settings > Companies > My Company > Update Info > Currency"

        full_message = "{}\n{}\n{}".format(message, message1, path)
        
        company = self.env.user.company_id
        if company.currency_id != self.env.ref('base.QAR'):
            raise exceptions.UserError(full_message)


    def open_wizard(self):
    #Check if no records exist in api.credentials.wizard
        if not self.env['api.credentials.wizard'].search_count([]):
            _logger.info("No Records exist in api.credentials.wizard.")

            # Get the action data
            action_data = self.env.ref('odoo_sadad_qa_invoice_integration.action_create_api_credentials').read()[0]

            # Create a new record in ir.actions.todo with the action data
            self.env['ir.actions.todo'].create({
                'action_id': action_data['id'],
                'sequence': 1,  # Adjust the sequence as needed
                # You may need to copy other fields from the action data depending on your requirements
            })

            _logger.info("ir.actions.todo created for api.credentials.wizard")

            return action_data
    
    @api.model
    def init(self):
        """
        Initialize the module.
        """
        self._check_company_currency()
        

    @api.model
    def post_init_hook(self):
        """
        Initialize the module.
        """
        _logger.info("self.open_wizard()")
        self.open_wizard()

    @api.model
    def validate_invoice_creation(self, vals_list):
        """
        Validate partner information, currency, and invoice lines before creating an invoice.
        """
        # Validation logic unchanged
        # Check if 'partner_id' is present in vals_list
        if 'partner_id' not in vals_list:
            raise exceptions.ValidationError("Partner and invoice lines are required for invoice creation.")

        # Retrieve the partner record based on 'partner_id' value
        partner = self.env['res.partner'].browse(vals_list['partner_id'])

        # Check if partner's name, phone number, and phone code are present
        if not partner.name or not partner.mobile or not partner.country_id.phone_code:
            raise exceptions.ValidationError("Partner's name, phone number, and phone code are required for invoice creation.")

        PHONE_LENGTH = 10
        # Check if the phone number is in the correct format
        if not (partner.mobile and str(partner.mobile).isdigit() and len(partner.mobile) == PHONE_LENGTH):
            raise exceptions.ValidationError(f"Invalid phone number format: {partner.mobile}")

        # Check if the phone code is in the correct format (assuming it's a 2-digit code)
        if not (partner.country_id.phone_code and str(partner.country_id.phone_code).isdigit() and len(str(partner.country_id.phone_code)) == 2):
            raise exceptions.ValidationError(f"Invalid phone code format: {partner.country_id.phone_code}")

        # Check if the currency is set to QAR
        if 'currency_id' in vals_list and vals_list.get('currency_id') != self.env.ref('base.QAR').id:
            raise exceptions.UserError("Currency must be set to QAR for invoice creation.")

        # Check if 'invoice_line_ids' is present and not empty
        if 'invoice_line_ids' not in vals_list or not vals_list['invoice_line_ids']:
            raise exceptions.ValidationError('Invoice lines are required for invoice creation.')
        
        # Prevent deletion of existing invoice lines
        if 'invoice_line_ids' in vals_list and vals_list['invoice_line_ids']:
            for line_id in vals_list['invoice_line_ids']:
                if line_id[0] == 2:
                    raise exceptions.ValidationError("Cannot delete existing invoice lines.")
        

    @api.model
    def create(self, vals_list):
        """
        Override create method to validate invoice creation and trigger actions.
        """
        self.validate_invoice_creation(vals_list)
        _logger.info(f'VALS : {vals_list}')
        _logger.info(f'Partner ID: {vals_list.get("partner_id")}')
        _logger.info(f'Invoice Line IDs: {vals_list.get("invoice_line_ids")}')

        records = super(InvoiceEventListener, self).create(vals_list)
        _logger.info(f"ADNANANANNAANANANANs {records}")
       
        for record in records:
            class_values = record.read()[0]
            _logger.info(f"Invoice creation triggered for record with ID {record.id}")
            _logger.info(f"Invoice creation triggered for record with ID {class_values}")
            
            self.perform_action_on_invoice_creation(record)
            
        return records


    @api.model
    def write(self, vals):
        """
        Override the write method to perform actions when an invoice is updated.
        """
         # Make a copy of the current record before it's updated
        previous_record = self.env[self._name].browse(self.ids)
        _logger.info(f"previous_record:{previous_record}") 
        _logger.info(f"previous_record:{previous_record.invoice_line_ids}")
        for line in previous_record.invoice_line_ids:
            _logger.info(f"Product Name:  {line.name}")
            _logger.info(f"Product Quantity:  {line.quantity}")
            _logger.info(f"Product Subtotal:  {line.price_subtotal}")

        # Extract account.move.line ids associated with the current invoice
        invoice_line_ids_previous = previous_record.invoice_line_ids
        
        _logger.info(f"invoice_line_ids{invoice_line_ids_previous}")
        
        res = super(InvoiceEventListener, self).write(vals)
        

        for record in self:
            _logger.info(record)
            if record and vals:
                if any(field in vals for field in ['partner_id', 'invoice_line_ids', 'payment_state']):  
                #if 'state' in vals and vals['state'] == 'posted': #Check status of invoice before create 
                # If the state of the invoice is changed to 'posted', trigger the update API call
                    _logger.info("If the state of the invoice is changed to 'posted', trigger the update API call")
                   
                    self.perform_action_on_invoice_update(record, invoice_line_ids_previous)
                #continue

        return res
        
    @api.model
    def perform_action_on_invoice_update(self, record, invoice_line_ids_previous):
        """
        Perform actions upon updating an invoice.
        """
        auth_token = self.authenticate_sadad_api()
        if auth_token:
            existing_sadad_invoice = self.env['sadad.api.response'].search([('invoice_id', '=', record.id)], limit=1)
            if existing_sadad_invoice:
                _logger.info("Update invoice sadad api perform")
                try:     
                    self.update_invoice_sadad_api(auth_token, record, invoice_line_ids_previous)
                except Exception as e:
                    _logger.error(f"Error updating invoice via SADAD API: {e}")
            else:
                _logger.info("Create invoice sadad api perform")
                try:
                    self.create_invoice_sadad_api(auth_token, record)
                except Exception as e:
                    _logger.error(f"Error creating invoice via SADAD API: {e}")
        else:
            _logger.error("Authentication token does not exist or is invalid")


   
    @api.model
    def perform_action_on_invoice_creation(self, record):
        """
        Perform actions upon invoice creation.
        """
        auth_token = self.authenticate_sadad_api()
        if auth_token:
            existing_sadad_invoice = self.env['sadad.api.response'].search([('invoice_id', '=', record.id)], limit=1)
            if existing_sadad_invoice: 
                _logger.info("Update invoice sadad api")
            else:
                _logger.info("Create invoice sadad api")
                self.create_invoice_sadad_api(auth_token, record)
        else:
            _logger.info(f"Authentication token does not exist: {auth_token}")

    @api.model
    def authenticate_sadad_api(self):
        """
        Authenticate with the SADAD API.
        """
        sadad_credentials = self.env['api.credentials.wizard'].search([], limit=1)

        if not sadad_credentials:
            _logger.error("SADAD credentials not found. Unable to perform authentication.")
            return None

        auth_url = "https://api-s.sadad.qa/api/userbusinesses/login"
        auth_payload = {
            "sadadId": sadad_credentials.sadad_id,
            "secretKey": sadad_credentials.secret_key,
            "domain": sadad_credentials.domain
        }
        auth_headers = {'Content-Type': 'application/json'}

        try:
            auth_response = requests.post(auth_url, headers=auth_headers, json=auth_payload)
            auth_response.raise_for_status()
            auth_token = auth_response.json().get('accessToken')

            if auth_token:
                _logger.info("Authentication to SADAD API successful")
                _logger.info("Authentication to SADAD API successful")
                return auth_token
            else:
                _logger.error("Authentication to SADAD API failed")
                return None

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error during authentication to SADAD API: {e}")
            return None

    @api.model
    def create_invoice_sadad_api(self, auth_token, record):
        """
        Create invoice using SADAD API.
        """
        create_invoice_url = "https://api-s.sadad.qa/api/invoices/createInvoice"

        _logger.info(f"phone_code:  {record.partner_id.country_id.phone_code}")
        _logger.info(f"phone  {record.partner_id.mobile}")
        _logger.info(f"name  {record.partner_id.name}")
        #_logger.info(f"invoice_line_ids:  {record.invoice_lin_ids}")
        
        for line in  record.invoice_line_ids:
            _logger.info(f"Product Name:  {line.name}")
            _logger.info(f"Product Quantity:  {line.quantity}")
            _logger.info(f"Product Subtotal:  {line.price_subtotal}")
        
        _logger.info(f"invoice_line_ids:  {record.invoice_line_ids}")
        _logger.info(f"state:  {record.state}")
        _logger.info(f"remark:  {record.highest_name}")
        _logger.info(f"Total Amouont:  {record.amount_total}")
        _logger.info(f"Display Name: {record.display_name}")
        _logger.info(f"Highest Name: {record.highest_name}")

        invoice_payload = {
            "countryCode": record.partner_id.country_id.phone_code,
            "cellnumber": record.partner_id.mobile,
            "clientname": record.partner_id.name,
            "invoicedetails": [
                {
                    "description": line.name,
                    "quantity": line.quantity,
                    "amount": line.price_subtotal
                } for line in record.invoice_line_ids],
            "status": 2 if record.payment_state == 'not_paid' else (3 if record.payment_state == 'paid' else 1),
            "remarks": record.highest_name,
            "amount": record.amount_total
        }
        
        _logger.info(f"invoice_payload: {invoice_payload}")
        
        invoice_headers = {'Authorization': auth_token, 'Content-Type': 'application/json'} 

        try:
            invoice_response = requests.post(create_invoice_url, headers=invoice_headers, json=invoice_payload)
            invoice_response.raise_for_status()

            if invoice_response.status_code == 200:
                _logger.info("Invoice created successfully via SADAD API")
                _logger.info(f"Invoice Response: {invoice_response.content}")

                invoice_details = invoice_response.json() 
                
                _logger.info(f"invoice_details{invoice_details[0].get('invoicedetails')}")
                _logger.info(f"Invoice created successfully for {record.highest_name}")
                self.store_api_response(record, invoice_response)
                
            else:
                _logger.warning(f"Failed to create invoice via SADAD API. Status code: {invoice_response.status_code}")

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error during create invoice API call to SADAD API: {e}")

    @api.model
    def store_api_response(self, record, invoice_response):
        """
        Store SADAD API response in Odoo database.
        """
        try:
            if invoice_response.status_code == 200:
                api_response_data = invoice_response.json()

                invoice_no = api_response_data[0].get("invoiceno")
                invoice_id = api_response_data[0].get("id")


                _logger.info(f"invoice_no:  {invoice_no}")
                _logger.info(f"invoice_id:  {invoice_id}")
                                

                if invoice_no and invoice_id:
                    existing_response = self.env['sadad.api.response'].search([('invoice_number', '=', invoice_no)], limit=1)
                    if existing_response:
                        existing_response.write({
                            'invoice_id': record.id,
                            'sadad_invoice_id': invoice_id
                        })
                        _logger.info(f"Updated existing Sadad API response for invoice number: {invoice_no}")
                    else:
                        api_response = self.env['sadad.api.response'].create({
                        'invoice_id': record.id,
                        'invoice_number': invoice_no,
                        'sadad_invoice_id': invoice_id
                    })
                    _logger.info(f"Sadad API response stored for invoice number: {invoice_no}")
                    _logger.info(f"Sadad API response stored for invoice id: {invoice_id}")

                    # Call _compute_sadad_response_id after successfully storing the API response
                    record._compute_sadad_response_id()

                    return api_response
                else:
                    _logger.error("Invoice number not found in the API response data")

            else:
                _logger.error(f"ERROR: Unexpected response status code {invoice_response.status_code}")
        except Exception as e:
            _logger.error(f"Error storing API response: {e}")

    @api.model
    def update_invoice_sadad_api(self, auth_token, record, invoice_line_ids_previous):
        """
        Update invoice using SADAD API.
        """
        _logger.info("-------------------------------------------------------------------UPDATE INVOICE DATA-------------------------------------------------------------------")
        _logger.info(f"phone_code:  {record.partner_id.country_id.phone_code}")
        _logger.info(f"phone  {record.partner_id.mobile}")
        _logger.info(f"name  {record.partner_id.name}")
        
        for line in  record.invoice_line_ids:
            _logger.info(f"Product Name:  {line.name}")
            _logger.info(f"Product Quantity:  {line.quantity}")
            _logger.info(f"Product Subtotal:  {line.price_subtotal}")
        
        _logger.info(f"invoice_line_ids:  {record.invoice_line_ids}")
        _logger.info(f"payment_state:  {record.payment_state}")
        _logger.info(f"state:  {record.state}")
        _logger.info(f"remark:  {record.highest_name}")
        _logger.info(f"Total Amouont:  {record.amount_total}")
        _logger.info(f"Display Name: {record.display_name}")
        _logger.info(f"Highest Name: {record.highest_name}")

        _logger.info(f"invoice_line_ids_previous : {invoice_line_ids_previous}")
        
        new_invoice_line_ids = list(set(record.invoice_line_ids).difference(set(invoice_line_ids_previous)))
        _logger.info(f"new_invoice_line_ids: {new_invoice_line_ids}")



        update_invoice_url = "https://api-s.sadad.qa/api/invoices/updateInvoice"

        sadad_response = self.env['sadad.api.response'].search([('invoice_id', '=', record.id)], limit=1)        
        sadad_invoice_details_id = self.env['sadad.invoice.details'].search([('invoice_id', '=', record.id)], limit=1)

        _logger.info(f"sadad_invoice_details_id.sadad_invoice_details_id{sadad_invoice_details_id.sadad_invoice_details_id}")
        # Extract sadad_invoice_id from the sadad.api.response record
        sadad_invoice_id = sadad_response.sadad_invoice_id
        _logger.info(f"sadad_invoice_id: {sadad_invoice_id}")
        
        if sadad_response:

            update_payload = {
                "clientname": record.partner_id.name,
                #"invoicedetails":updated_invoice_lines,
                "invoicedetails": [
                    {
                        "description": line.name,
                        "quantity": line.quantity,
                        "amount": line.price_subtotal,
                        "invoiceId": sadad_invoice_id
                    } for line in new_invoice_line_ids
                    ],
                "amount": record.amount_total,
                "status": 2 if record.payment_state == 'not_paid' else (3 if record.payment_state == 'paid' else 1) ,
                "id": sadad_invoice_id
                }
            _logger.info(f"update_payload: {update_payload}")

            update_headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}

            try:
                invoice_response = requests.patch(update_invoice_url, headers=update_headers, json=update_payload)
                invoice_response.raise_for_status()

                if invoice_response.status_code == 200:
                    _logger.info("Invoice updated successfully via SADAD API")
                    _logger.info(f"Updated Invoice Response Content: {invoice_response.content}")
                    #self.store_api_response(record, invoice_response)
                else:
                    _logger.warning(f"Failed to update invoice via SADAD API. Status code: {invoice_response.status_code}")

            except requests.exceptions.RequestException as e:
                if invoice_response.status_code == 403:  # If the update API returns a 403 status code
                    error_message = invoice_response.json().get("error", {}).get("message")
                    _logger.info(f"Updated Invoice Response Content: {invoice_response.content}")
                    _logger.warning(f"Failed to update invoice: {error_message}")
                    raise exceptions.UserError(error_message)
                    
                else:
                    _logger.error(f"Error during update invoice API call to SADAD API: {e}")
                    _logger.info(f"Updated Invoice Response Content: {invoice_response.content}")
        else:
            _logger.warning("No matching sadad.api.response record found for invoice")


