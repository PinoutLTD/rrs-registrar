import typing as tp

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