import typing as tp
from dotenv import load_dotenv
import os

from helpers.pinata import PinataHelper
from utils.decryption import decrypt_message
from helpers.logger import Logger

from registar.utils.messages import (message_with_pinata_creds, 
                                     message_with_robonomics_address)
load_dotenv()
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

class MessageManager:

    def __init__(self, odoo):
        self.odoo = odoo
        self._logger = Logger("MessageManager")

    def select_formatter(self, msg) -> str:
        if "new_client" in msg:
            sender_address = msg["new_client"]
            return message_with_robonomics_address(sender_address)
        if "email" in msg:
            sender_address = msg["address"]
            email = self._decrypt_email(msg)
            rrs_user_id = self.odoo.check_if_rrs_user_exists(sender_address)
            if rrs_user_id:
                pinata_key, pinata_secret = self._get_existing_user_credentials(sender_address, rrs_user_id)
                paid = self.odoo.is_paid(rrs_user_id)
            else:
                user_id = self._create_new_rrs_user(email, sender_address)
                pinata_key, pinata_secret = self._generate_and_store_pinata_keys(user_id, sender_address)
                paid = False
                
            return message_with_pinata_creds(pinata_key, pinata_secret, sender_address, self._logger, paid)

    
    def _decrypt_email(self, msg: dict) -> str:
        return decrypt_message(msg["email"], msg["address"], self._logger)

    def _get_existing_user_credentials(self, sender_address, rrs_user_id):
        """Retrieves and sends Pinata credentials for an existing user."""
        pinata_key, pinata_secret = self.odoo.retrieve_pinata_creds(sender_address, rrs_user_id)
        if pinata_key:
            return pinata_key, pinata_secret

    def _create_new_rrs_user(self, decrypted_email, sender_address):
        """Creates a new RRS user and returns the user ID."""
        return self.odoo.create_rrs_user(decrypted_email, sender_address)

    def _generate_and_store_pinata_keys(self, user_id, sender_address):
        """Generates Pinata credentials and updates the RRS user with them."""
        pinata_keys = PinataHelper.generate_pinata_keys(sender_address)
        pinata_key = pinata_keys["pinata_api_key"]
        pinata_secret = pinata_keys["pinata_api_secret"]
        
        self._logger.debug(f"Generated Pinata creds: {pinata_key}, {pinata_secret}")
        self.odoo.update_rrs_user_with_pinata_creds(user_id, pinata_key, pinata_secret)
        return pinata_key, pinata_secret