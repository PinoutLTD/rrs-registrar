from dotenv import load_dotenv
import os
import base64
import xmlrpc.client
import typing as tp
from datetime import datetime
from utils.logger import Logger
from utils.read_file import read_file

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
ODOO_PRODUCT_SUBSCRIPTION_ID = os.getenv("ODOO_PRODUCT_SUBSCRIPTION_ID")
SUBSCRIPTION_PRICE = os.getenv("SUBSCRIPTION_PRICE")
STATUS_NOTPAID_ID = os.getenv("ODOO_RRS_STATUS_NOTPAID_ID")
STATUS_PAID_ID = os.getenv("ODOO_RRS_STATUS_PAID_ID")


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

    def create_rrs_user(self, email: str, owner_address: str, controller_address: str) -> tp.Optional[int]:
        """Creates user in Robonomics Report Service module  and returns its id.
        :param email: Customer's email address
        :param owner_address: Customer's address in Robonomics parachain
        :param controller_address: Controller's address in Robonomics parachain

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
                        "address": owner_address,
                        "customer_email": email,
                        "status": STATUS_NOTPAID_ID,
                        "subscription": False,
                        "controller_address": controller_address,
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

    def _check_if_customer_exists(self, address: str) -> tp.Union[int, bool]:
        """Looking for a partner id by the parachain address. This id is used in `create_invoice` function to
        add a `customer` field.
        :param address: Customer's address in Robonomics parachain

        :return: The partner id or false.
        """
        id = self._connection.execute_kw(
            ODOO_DB, self._uid, ODOO_PASSWORD, "res.partner", "search", [[("name", "=", address)]]
        )
        self._logger.debug(f"Find ustomer with id: {id}")
        return id

    def create_customer(self, email: str, address: str) -> tp.Optional[int]:
        try:
            customer_id = self._check_if_customer_exists(address)
            if customer_id:
                return customer_id[0]
            customer_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "res.partner",
                "create",
                [
                    {
                        "name": address,
                        "is_company": False,
                        "email": email,
                    }
                ],
            )
            self._logger.debug(f"Create customer with id: {customer_id}")
            return customer_id
        except Exception as e:
            self._logger.error(f"Couldn't create customer: {e}")
            return None

    def create_invoice(self, address: str, customer_id: str) -> tp.Optional[int]:
        """Creates invoice in Invoicing module.
        :param address: Customer's address in Robonomics parachain for the reference

        :return: Invoice id
        """
        try:
            line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": ODOO_PRODUCT_SUBSCRIPTION_ID,
                        "name": "Robonomics Subscription 1 month",
                        "quantity": 1,
                        "price_unit": SUBSCRIPTION_PRICE,
                    },
                )
            ]

            invoice_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "account.move",
                "create",
                [
                    (
                        {
                            "partner_id": customer_id,
                            "ref": address,
                            "move_type": "out_invoice",
                            "invoice_date": str(datetime.today().date()),
                            "line_ids": line_ids,
                        }
                    )
                ],
            )
            self._logger.debug(f"Create invoice with id: {invoice_id}")
            return invoice_id
        except Exception as e:
            self._logger.error(f"Couldn't create invoice: {e}")
            return None

    def post_invoice(self, invoice_id: int) -> bool:
        """Post the invoice in Invoicing module.
        :param invoice_id: Invoice id
        :return: bool
        """
        return self._connection.execute_kw(
            ODOO_DB, self._uid, ODOO_PASSWORD, "account.move", "write", [[invoice_id], {"state": "posted"}]
        )

    def update_rrs_user_with_pinata_creds(self, user_id: int, pinata_key: str, pinata_api_secret: str) -> bool:
        """Update the customer profile with pinata credentials in RRS module.
        :param customer_id: User id
        :param pinata_key: Pinata API key
        :param pinata_api_secret: Pinata API secret key
        :return: bool
        """
        return self._connection.execute_kw(
            ODOO_DB,
            self._uid,
            ODOO_PASSWORD,
            "rrs.register",
            "write",
            [
                [user_id],
                {
                    "pinata_key": pinata_key,
                    "pinata_secret": pinata_api_secret,
                    "started_date": str(datetime.today().date()),
                },
            ],
        )
