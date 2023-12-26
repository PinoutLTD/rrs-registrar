from flask import request
from flask_classful import FlaskView, route
from dotenv import load_dotenv
import os
import threading
import json

from utils.logger import Logger
from utils.pinata import generate_pinata_keys
from utils.decrypt_encrypt_msg import encrypt_message
from utils.robonomics import transfer_xrt_2buy_subscription

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
STATUS_PAID_ID = os.getenv("ODOO_RRS_STATUS_PAID_ID")
ADMIN_SEED = os.getenv("ADMIN_SEED")


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
        print(f"self 2: {self}")
        request_data = request.get_json()
        self._logger.debug(f"Data from request: {request_data}")
        if "status" in request_data.keys():
            status_id = int(request_data["status"])
            if status_id == int(STATUS_PAID_ID):
                id = int(request_data["id"])
                owner_address = request_data["address"]
                controller_address = str(request_data["controller_address"])
                pinata_keys = generate_pinata_keys(PINATA_API_KEY, PINATA_API_SECRET, owner_address)
                threading.Thread(
                    target=self.handle_data_from_request, args=(id, pinata_keys, controller_address, owner_address)
                ).start()
        return "ok"

    def handle_data_from_request(self, user_id: int, pinata_keys: dict, controller_address: str, owner_address: str):
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
            transfer_xrt_2buy_subscription(owner_address)
        except Exception as e:
            print(f"Couldn't transfer XRT: {e}")