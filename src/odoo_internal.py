from dotenv import load_dotenv
import os
import xmlrpc.client
import typing as tp
from utils.logger import Logger
from utils.read_file import read_file

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_PRODUCT_SABSCRIPTION_ID = os.getenv("ODOO_PRODUCT_SABSCRIPTION_ID")

class OdooHelper:
    def __init__(self):
        self._logger = Logger("odoo")
        self._connection, self._uid = self._connect_to_db()

    def _connect_to_db(self):
        """Connect to Odoo db

        :return: Proxy to the object endpoint to call methods of the odoo models.
        """
        try:
            common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(ODOO_URL), allow_none=1)
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if uid == 0:
                raise Exception("Credentials are wrong for remote system access")
            else:
                self._logger.debug("Connection Stablished Successfully")
                connection = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(ODOO_URL))
                return connection, uid
        except Exception as e:
            self._logger.error(f"Couldn't connect to the db: {e}")

    def create_rrs_user(self, email: str, robonomics_address: str) -> tp.Optional[int]:
        """Creates user in Robonomics Report Service module  and returns its id.
        :param email: Customer's email address
        :param robonomics_address: Customer's address in Robonomics parachain

        :return: User id
        """
        try:
            user_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "rrs.register",
                "create",
                [
                    {
                        "address": robonomics_address,
                        "customer_email": email,
                    }
                ],
            )
            return user_id
        except Exception as e:
            self._logger.error(f"Couldn't create ticket: {e}")
            return None

    def create_ticket(self, email: str, robonomics_address: str, phone: str, description: str) -> tp.Optional[int]:
        """Creates ticket in Helpdesk module

        :param email: Customer's email address
        :param robonomics_address: Customer's address in Robonomics parachain
        :param phone: Customer's phone number
        :param description: Problem's description from cusotmer

        :return: Ticket id
        """

        priority = "3"
        channel_id = 5
        name = f"Issue from {robonomics_address}"
        description = f"Issue from HA: {description}"
        try:
            ticket_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "helpdesk.ticket",
                "create",
                [
                    {
                        "name": name,
                        "description": description,
                        "priority": priority,
                        "channel_id": channel_id,
                        "partner_email": email,
                        "phone": phone,
                    }
                ],
            )
            return ticket_id
        except Exception as e:
            self._logger.error(f"Couldn't create ticket: {e}")
            return None
    
    def create_note_with_attachment(self, ticket_id: int, file_name: str, file_path: str) -> tp.Optional[bool]:
        """Create log with attachment in Odoo using logs from the customer

        :param ticket_id: Id of the ticket to which logs will be added
        :param file_name: Name of the file
        :param file_path: Path to the file

        :return: If the log note was created or no
        """
        data = read_file(file_path)
        try:
            record = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "mail.message",
                "create",
                [
                    {
                        "body": "Logs from user",
                        "model": "helpdesk.ticket",
                        "res_id": ticket_id,
                    }
                ],
            )
            attachment = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "ir.attachment",
                "create",
                [
                    {
                        "name": file_name,
                        "datas": base64.b64encode(data).decode(),
                        "res_model": "helpdesk.ticket",
                        "res_id": ticket_id,
                    }
                ],
            )
            return self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "mail.message",
                "write",
                [[record], {"attachment_ids": [(4, attachment)]}],
            )
        except Exception as e:
            self._logger.error(f"Couldn't create note: {e}")
            return None
    
    def create_invoice(self, address: str) -> tp.Optional[int]:
        """Creates invoice in Invoicing module.
        :param address: Customer's address in Robonomics parachain for the reference
        
        :return: Invoice id
        """
        try:
            line_ids = [(
                            0,
                            0,
                            {
                                "product_id": ODOO_PRODUCT_SABSCRIPTION_ID,
                                "quantity": 1,
                            },
                        )]

            invoice_id = self.connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "account.move",
                "create",
                [
                    (
                        {   "ref": address,
                            "move_type": "out_invoice",
                            "invoice_date": str(datetime.today().date()),
                            "line_ids": line_ids
                        }
                    )
                ],
            )
            self._logger.debug(f"Create invoice with id: {invoice_id}")
        except Exception as e:
            self._logger.error(f"Couldn't create invoice: {e}")
            return None