from flask import request
from flask_classful import FlaskView, route
from dotenv import load_dotenv
import os
import threading
import json

from utils.logger import Logger
from utils.pinata import generate_pinata_keys, revoke_pinata_key, unpin_hash_from_pinata
from utils.decrypt_encrypt_msg import encrypt_message
from utils.robonomics import transfer_xrt_2buy_subscription
from utils.parse_string import extract_hash

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
STATUS_PAID_ID = os.getenv("ODOO_RRS_STATUS_PAID_ID")
STATUS_NOTPAID_ID = os.getenv("ODOO_RRS_STATUS_NOTPAID_ID")
ADMIN_SEED = os.getenv("ADMIN_SEED")
DONE_SATGE_ID = os.getenv("ODOO_HELPDESK_DONE_STAGE_ID")


class BaseView(FlaskView):
    odoo = None
    ws = None
    _logger = None

    @classmethod
    def initialize(cls, odoo, ws_client):
        cls.odoo = odoo
        cls.ws_client = ws_client
        cls.set_logger()

    @classmethod
    def set_logger(cls):
        cls._logger = Logger("flask")


class OdooFlaskView(BaseView):
    def index(self):
        return "<h1>Welcome from Flask</h1>"

    @route("/rrs/payment", methods=["POST"])
    def payment_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from payment request: {request_data}")
        if "status" in request_data.keys():
            status_id = int(request_data["status"])
            if status_id == int(STATUS_PAID_ID):
                id = int(request_data["id"])
                controller_address = request_data["address"]
                owner_address = str(request_data["owner_address"])
                pinata_keys = generate_pinata_keys(PINATA_API_KEY, PINATA_API_SECRET, owner_address)
                threading.Thread(
                    target=self._odoo_request_add_pinata_creds,
                    args=(id, pinata_keys, controller_address, owner_address),
                ).start()
        return "ok"

    def _odoo_request_add_pinata_creds(
        self, user_id: int, pinata_keys: dict, controller_address: str, owner_address: str
    ):
        pinata_key = pinata_keys["pinata_api_key"]
        pinata_secret = pinata_keys["pinata_api_secret"]
        self.odoo.update_rrs_user_with_pinata_creds(user_id, pinata_key, pinata_secret)
        pinata_key_encrypted = encrypt_message(pinata_key, ADMIN_SEED, controller_address)
        pinata_secret_encrypted = encrypt_message(pinata_secret, ADMIN_SEED, controller_address)
        msg = {
            "protocol": f"/pinataCreds/{controller_address}",
            "serverPeerId": "",
            "data": {"public": pinata_key_encrypted, "private": pinata_secret_encrypted},
        }
        self.ws_client.ws.send(json.dumps(msg))
        try:
            transaction_hash = transfer_xrt_2buy_subscription(owner_address)
            if transaction_hash:
                self._logger.debug(f"XRT has been sent to ${owner_address}")
                self.odoo.update_rrs_user_with_subscription_status(user_id)
                self.ws_client.ws.send(json.dumps(msg))
        except Exception as e:
            self._logger.error(f"Couldn't transfer XRT: {e}")

    @route("/rrs/expired", methods=["POST"])
    def expired_subscription_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from expired request: {request_data}")
        if "status" in request_data.keys():
            status_id = int(request_data["status"])
            if status_id == int(STATUS_NOTPAID_ID):
                pinata_key = request_data["pinata_key"]
                id = request_data["id"]
                pinata_response = revoke_pinata_key(PINATA_API_KEY, PINATA_API_SECRET, pinata_key)
                if pinata_response == {"message": "Revoked"}:
                    self._logger.debug(f"Succesfully removed key {pinata_key} from Pinata")
                    threading.Thread(target=self._odoo_request_revoke_pinata_creds, args=(id,)).start()
                else:
                    self._logger.error(f"Couldn't remove key {pinata_key} from Pinata. Response: {pinata_response}")
        return "ok"

    def _odoo_request_revoke_pinata_creds(self, user_id: int) -> None:
        self.odoo.revoke_pinata_creds_from_rss_user(user_id)

    @route("/helpdesk/ticket-done", methods=["POST"])
    def ticket_done_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from ticket-done request: {request_data}")
        if int(request_data["stage"]) == int(DONE_SATGE_ID):
            description = request_data["description"]
            hash = extract_hash(description)
            if hash:
                pinata_response = unpin_hash_from_pinata(PINATA_API_KEY, PINATA_API_SECRET, hash)
                if pinata_response == {"message": "Removed"}:
                    self._logger.debug(f"Succesfully removed hash {hash} from Pinata")
                else:
                    self._logger.error(f"Couldn't remove hash {hash} from Pinata. Response: {pinata_response}")
        return "ok"
