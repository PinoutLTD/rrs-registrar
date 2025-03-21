import typing as tp
from datetime import datetime

from tenacity import *

from helpers.logger import Logger
from helpers.odoo import OdooHelper


class Odoo:
    def __init__(self) -> None:
        self.helper = OdooHelper("registar")
        self._logger = Logger("odoo-registar")

    @retry(wait=wait_fixed(5))
    def create_rrs_user(self, email: str, sender_address: str) -> tp.Optional[int]:
        """Creates user in Robonomics Report Service module  and returns its id.
        :param email: Customer's email address
        :param sender_address: Customer's address in Robonomics parachain

        :return: User id
        """
        try:
            user_id = self.helper.create(
                "rrs.register",
                {
                    "address": sender_address,
                    "customer_email": email,
                },
            )
            return user_id
        except Exception as e:
            self._logger.error(f"Couldn't create user: {e}")
            raise Exception("Failed to create rrs user")

    @retry(wait=wait_fixed(5))
    def check_if_rrs_user_exists(self, sender_address: str) -> tp.Union[int, bool]:
        """Looking for a rrs user id by the controller address.
        :param sender_address: Customer's address in Robonomics parachain.

        :return: The user id or false.
        """
        id = self.helper.search("rrs.register", [("address", "=", sender_address)])
        self._logger.debug(f"Find RRS user with id: {id}")
        if id:
            return id[0]
        return False

    @retry(wait=wait_fixed(5))
    def update_rrs_user_with_pinata_creds(self, user_id: int, pinata_key: str, pinata_api_secret: str) -> bool:
        """Update the customer profile with pinata credentials in RRS module.
        :param customer_id: User id
        :param pinata_key: Pinata API key
        :param pinata_api_secret: Pinata API secret key
        :return: bool
        """
        try: 
            return self.helper.update(
                "rrs.register",
                user_id,
                {
                    "pinata_key": pinata_key,
                    "pinata_secret": pinata_api_secret,
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update user {user_id} with pinata creds {e}")
            raise Exception("Failed to update the user")
    
    @retry(wait=wait_fixed(5))
    def retrieve_pinata_creds(self, sender_address: str, rrs_user_id: int) -> tuple:
        """Retrieve pinata creds.
        :param sender_address: Customer's address in Robonomics parachain
        :param rrs_user_id: User id in RRS module.

        :return: The Pinata creds or None.
        """
        try:
            rrs_user_data = self.helper.read("rrs.register", [rrs_user_id], ["pinata_key", "pinata_secret"])
            if rrs_user_data:
                pinata_key = rrs_user_data[0]["pinata_key"]
                pinata_secret = rrs_user_data[0]["pinata_secret"]
                self._logger.debug(f"Found pinata creds for address: {sender_address}, pinata key: {pinata_key}")
                return pinata_key, pinata_secret
            else:
                self._logger.error(f"Couldn't find pinata creds for {sender_address}")
        except Exception as e:
            self._logger.error(f"Couldn't get pinata creds for user: {sender_address}")
            raise Exception(f"Couldn't  retrieve pinata creds for {sender_address}")
        
    @retry(wait=wait_fixed(5))
    def is_paid(self, rrs_user_id: int) -> bool:
        """Check if the customer has paid for the service.
        :param address: rrs_user_id: User id in RRS module.

        :return: bool
        """
        return self.helper.read("rrs.register", [rrs_user_id], ["paid"])[0]["paid"]

    @retry(wait=wait_fixed(5))
    def save_cid_and_orderid(self, cid: str, order_id: str, email: str):
        id = self._find_user_by_email(email)
        if not id:
            self._logger.error(f"Couldn't user with email: {email}")
            return 
        try: 
            return self.helper.update(
                "rrs.register",
                id[0],
                {
                    "revolut_cid": cid,
                    "revolut_order_id": order_id,
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update user {id} with revolut: {e}")
            raise Exception("Failed to update the user")
        
    @retry(wait=wait_fixed(5))
    def save_orderid(self, cid: str, order_id: str):
        id = self._find_user_by_cid(cid)
        self._logger.debug(f"ORDER ID NEW: {order_id}")
        if not id:
            self._logger.error(f"Couldn't user with cid: {cid}")
            return 
        try: 
            return self.helper.update(
                "rrs.register",
                id[0],
                {
                    "revolut_order_id": order_id,
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update user {id} with order_id: {e}")
            raise Exception("Failed to update the user")
    
    @retry(wait=wait_fixed(5))
    def update_last_paid(self, order_id: str, id: int = None):
        if not id:
            id = self.find_user_by_orderid(order_id)
            if not id:
                self._logger.error(f"Couldn't user with order_id: {order_id}")
                return 
        try: 
            return self.helper.update(
                "rrs.register",
                id[0],
                {
                    "paid": True,
                    "last_paid": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update user {id} with last_paid: {e}")
            raise Exception("Failed to update the user")

    @retry(wait=wait_fixed(5))
    def set_status_not_paid(self, order_id: str):
        id = self.find_user_by_orderid(order_id)
        if not id:
            self._logger.error(f"Couldn't user with order_id: {order_id}")
            return 
        try: 
            return self.helper.update(
                "rrs.register",
                id[0],
                {
                    "paid": False
                },
            )
        except Exception as e:
            self._logger.error(f"Couldn't update user {id} with status not paid: {e}")
            raise Exception("Failed to update the user")
    

    @retry(wait=wait_fixed(5))
    def find_tickets_by_email(self, email: str):
        try:
            ticket_ids = self.helper.search(
                model="helpdesk.ticket", search_domains=[
                    ("partner_email", "=", email),
                ]
            )
            self._logger.debug(f"Ticket ids: {ticket_ids}")
            return ticket_ids
        except Exception as e:
            self._logger.error(f"Couldn't get tickets for {email}: {e}")
            raise Exception("Failed to get tickets")

    @retry(wait=wait_fixed(5))
    def delete_ticket(self, ticket_id: int):
        try:
            self._logger.debug("deleting ticket...")
            return self.helper.unlink("helpdesk.ticket", [ticket_id])
        except Exception as e:
            self._logger.error(f"Couldn't unlink ticket {ticket_id}: {e}")
            raise Exception("Failed to unlink ticket")
    
    @retry(wait=wait_fixed(5))
    def find_email_from_user_id(self, id: int):
        try:
            user_data = self.helper.read(model="rrs.register", record_ids=id, fields=["customer_email"])
            email = user_data[0]['customer_email']
            self._logger.debug(f"Find user's email: {email}")
            return email
        except Exception as e:
            self._logger.error(f"Couldn't find email for {id}: {e}")
            raise Exception("Failed to find email")
        

    @retry(wait=wait_fixed(5))
    def _find_user_by_email(self, email: str) -> list:
        """Find a user id by an email.
        :param address: User's email

        :return: The list with user id.
        """
        id = self.helper.search(model="rrs.register", search_domains=[("customer_email", "=", email)])
        self._logger.debug(f"Find user with id: {id}")
        return id
    
    @retry(wait=wait_fixed(5))
    def _find_user_by_cid(self, cid: str) -> list:
        """Find a user id by an email.
        :param address: User's email

        :return: The list with user id.
        """
        id = self.helper.search(model="rrs.register", search_domains=[("revolut_cid", "=", cid)])
        self._logger.debug(f"Find user with id: {id}")
        return id

    @retry(wait=wait_fixed(5))
    def find_user_by_orderid(self, order_id: str) -> list:
        """Find a user id by an email.
        :param address: User's email

        :return: The list with user id.
        """
        id = self.helper.search(model="rrs.register", search_domains=[("revolut_order_id", "=", str(order_id))])
        self._logger.debug(f"Find user with id: {id}")
        return id