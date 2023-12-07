from dotenv import load_dotenv
import os
import xmlrpc.client
import base64
from utils.logger import Logger
from tenacity import *


load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")


class OdooHelper:
    def __init__(self) -> None:
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

    
    def create_rrs_user(self, email, robonomics_address):
        self._logger.debug("Creating user...")
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
            self._logger.debug(f"User created. User id: {user_id}")
            return user_id
        except Exception as e:
            self._logger.error(f"Couldn't create user: {e}")
            return None

    
    @retry(wait=wait_fixed(5))
    def create_ticket(self, email, robonomics_address_from, phone, description):
        """Creating ticket until it will be created."""
        
        self._logger.debug("Creating ticket...")
        ticket_id = self._create_ticket(email, robonomics_address_from, phone, description)
        self._logger.debug(f"Ticket created. Ticket id: {ticket_id}")
        if not ticket_id:
            raise Exception("Failed to create ticket")
        return ticket_id

    def _create_ticket(self, email: str, robonomics_address: str, phone: str, description: str) -> int:
        """Internal methods. Creates ticket in Helpdesk module

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
            print(e)
            return None

    def _read_file(self, file_path: str) -> bytes:
        """Read file and return its content

        :param file_path: Path to the file to read
        :return: File's content in bytes
        """

        with open(file_path, "rb") as f:
            data = f.read()
        return data

    def create_note_with_attachment(self, ticket_id: int, file_name: str, file_path: str) -> bool:
        """Create log with attachment in Odoo using logs from the customer

        :param ticket_id: Id of the ticket to which logs will be added
        :param file_name: Name of the file
        :param file_path: Path to the file

        :return: If the log note was created or no
        """
        data = self._read_file(file_path)
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
