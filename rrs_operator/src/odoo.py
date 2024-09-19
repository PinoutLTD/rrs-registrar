import base64
import typing as tp

from tenacity import *

from helpers.logger import Logger
from helpers.odoo import OdooHelper
from rrs_operator.utils.format_hash_str import format_hash
from dotenv import load_dotenv
import os

load_dotenv()
ODOO_HELPDESK_NEW_STAGE_ID = os.getenv("ODOO_HELPDESK_NEW_STAGE_ID")
ODOO_HELPDESK_INPROGRESS_STAGE_ID = os.getenv("ODOO_HELPDESK_INPROGRESS_STAGE_ID")
ODOO_LOGS_LINK_FORMAT = os.getenv("ODOO_LOGS_LINK_FORMAT")


class Odoo:
    """Odoo for Operator"""
    def __init__(self) -> None:
        self.helper = OdooHelper("operator")
        self._logger = Logger("odoo-registar")

    @retry(wait=wait_fixed(5))
    def create_ticket(
        self, email: str, robonomics_address: str, description: str, priority: str, source: str
    ) -> tp.Optional[int]:
        """Creates ticket in Helpdesk module

        :param email: Customer's email address
        :param robonomics_address: Customer's address in Robonomics parachain
        :param description: Problem's description from cusotmer
        :param priority: Priority rating based on report type

        :return: Ticket id
        """

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
                    "source": source,
                    "count": 1
                },
            )
            self._logger.debug(f"Ticket created. Ticket id: {ticket_id}")
            return ticket_id
        except Exception as e:
            self._logger.error(f"Couldn't create ticket: {e}")
            raise Exception("Failed to create ticket")
    
    @retry(wait=wait_fixed(5))
    def create_note_with_logs_hash(self, ticket_id: int, ipfs_hash: str) -> None:
        try:
            record = self.helper.create(
                model="mail.message",
                data={
                    "body": f"https://demo.iotlab.cloud/tg/rrs/ipfs/{ipfs_hash}",
                    "model": "helpdesk.ticket",
                    "res_id": ticket_id,
                },
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

    def find_ticket_with_description(self, description: str, email: str) -> int:
        """ """
        description = f"Issue from HA: {description}"
        self._logger.debug(f"Looking for a ticket for email: {email}, description: {description}")
        ticket_ids = self.helper.search(
            model="helpdesk.ticket", search_domains=[
                ("description", "=", description), 
                ("partner_email", "=", email), 
                ("stage_id", "in", [int(ODOO_HELPDESK_NEW_STAGE_ID), int(ODOO_HELPDESK_INPROGRESS_STAGE_ID)])
            ]
        )
        self._logger.debug(f"Ticket ids: {ticket_ids}")

        if ticket_ids:
            self._logger.debug(f"Found tickets with the description: {ticket_ids}")
            return ticket_ids[0]
        self._logger.debug(f"No ticket found")

    def find_ticket_with_source(self, source: str, email: str) -> int:
        """ """
        self._logger.debug(f"Looking for a ticket for email: {email}, source: {source}")
        ticket_ids = self.helper.search(
            model="helpdesk.ticket", search_domains=[
                ("source", "=", str(source)), 
                ("partner_email", "=", email),
                ("stage_id", "in", [int(ODOO_HELPDESK_NEW_STAGE_ID), int(ODOO_HELPDESK_INPROGRESS_STAGE_ID)])
            ]
        )
        
        self._logger.debug(f"Ticket ids: {ticket_ids}")

        if ticket_ids:
            self._logger.debug(f"Found tickets with the source: {ticket_ids}")
            return ticket_ids[0]
        self._logger.debug(f"No ticket found")

    @retry(wait=wait_fixed(5))
    def get_hashes_from_ticket(self, ticket_id: int) -> list:
        self._logger.debug(f"Looking for ipfs hashes in ticket {ticket_id}")
        message_ids = self.helper.search(model="mail.message", search_domains=[("model", "=", "helpdesk.ticket"), ("res_id", "=", ticket_id)])
        messages = self.helper.read(model="mail.message", record_ids=[message_ids], fields=["id", "body"])
        hashes = [msg["body"] for msg in messages if msg["body"].startswith(f"<p>{ODOO_LOGS_LINK_FORMAT}Qm")]
        hashes = [format_hash(hash) for hash in hashes]
        return hashes
    
    @retry(wait=wait_fixed(5))
    def get_and_increase_problem_counter(self, ticket_id: int):
        counter = self.helper.read("helpdesk.ticket", [ticket_id], ["count"])[0]["count"]
        self._logger.debug(f"Updating counter for ticket {ticket_id}... Current counter is: {counter}")
        try: 
            return self.helper.update(
                "helpdesk.ticket",
                ticket_id,
                {
                    "count": int(counter)+1,
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update counter {e}")
            raise Exception("Failed to update counter")
        
    @retry(wait=wait_fixed(5))
    def get_and_update_description(self, ticket_id: int, new_description: str) -> bool:
        current_description = self.get_description_from_ticket(ticket_id)
        self._logger.debug(f"Updating description for ticket {ticket_id}... Current description is: {current_description}")
        try: 
            return self.helper.update(
                "helpdesk.ticket",
                ticket_id,
                {
                    "description": f"{current_description} {new_description}",
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update description {e}")
            raise Exception("Failed to update description")
    
    @retry(wait=wait_fixed(5))
    def get_description_from_ticket(self, ticket_id: int) -> str:
        description = self.helper.read("helpdesk.ticket", [ticket_id], ["description"])[0]["description"]
        return description