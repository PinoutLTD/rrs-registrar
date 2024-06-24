from helpers.odoo import OdooHelper
from helpers.logger import Logger
from tenacity import *
import typing as tp
import base64
from rrs_operator.utils.read_file import read_file


class Odoo:
    """Odoo for Operator"""
    def __init__(self) -> None:
        self.helper = OdooHelper("operator")
        self._logger = Logger("odoo-registar")

    @retry(wait=wait_fixed(5))
    def create_ticket(
        self, email: str, robonomics_address: str, phone: str, description: str, ipfs_hash: str
    ) -> tp.Optional[int]:
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
            ticket_id = self.helper.create(
                model="helpdesk.ticket",
                data={
                    "name": name,
                    "description": description,
                    "priority": priority,
                    "channel_id": channel_id,
                    "partner_email": email,
                    "phone": phone,
                },
            )
            self._logger.debug(f"Ticket created. Ticket id: {ticket_id}")
            return ticket_id
        except Exception as e:
            self._logger.error(f"Couldn't create ticket: {e}")
            raise Exception("Failed to create ticket")

    @retry(wait=wait_fixed(5))
    def create_note_with_attachment(self, ticket_id: int, file_name: str, file_path: str) -> tp.Optional[bool]:
        """Create log with attachment in Odoo using logs from the customer

        :param ticket_id: Id of the ticket to which logs will be added
        :param file_name: Name of the file
        :param file_path: Path to the file

        :return: If the log note was created or no
        """
        data = read_file(file_path)
        try:
            record = self.helper.create(
                model="mail.message",
                data={
                    "body": "Logs from user",
                    "model": "helpdesk.ticket",
                    "res_id": ticket_id,
                },
            )
            attachment = self.helper.create(
                model="ir.attachment",
                data={
                    "name": file_name,
                    "datas": base64.b64encode(data).decode(),
                    "res_model": "helpdesk.ticket",
                    "res_id": ticket_id,
                },
            )
            return self.helper.update(
                model="mail.message", record_id=record, data={"attachment_ids": [(4, attachment)]}
            )
        except Exception as e:
            self._logger.error(f"Couldn't create note: {e}")
            raise Exception("Failed to create note")

    @retry(wait=wait_fixed(5))
    def find_user_email(self, address) -> tp.Optional[str]:
        """Find the user's email.
        :param address: User's address in Robonomics parachain

        :return: The user email or None.
        """
        self._logger.debug(f"start looking for email.. {address}")
        try:
            user_id = self._find_user_id(address)
            self._logger.debug(f"user id: {user_id}")
            if user_id:
                user_data = self.helper.read(model="rrs.register", record_ids=user_id, fields=["customer_email"])
                email = user_data[0]['customer_email']
                self._logger.debug(f"Find user's email: {email}")
                return email
            else:
                self._logger.error(f"Couldn't find user for {address}")

        except Exception as e:
            self._logger.error(f"Couldn't find email {e}")
            raise Exception("Failed to find email")
    

    def _find_user_id(self, address: str) -> list:
        """Find a user id by the parachain address. This id is used to retrive the user's email.
        :param address: User's address in Robonomics parachain

        :return: The list with user id.
        """
        id = self.helper.search(model="rrs.register", search_domains=[("address", "=", address)])
        self._logger.debug(f"Find user with id: {id}")
        return id