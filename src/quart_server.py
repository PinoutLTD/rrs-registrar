from quart import Quart, request
import os
from dotenv import load_dotenv
import json
import asyncio

from utils.logger import Logger
from utils.pinata import generate_pinata_keys, revoke_pinata_key, unpin_hash_from_pinata
from utils.messages import message_with_pinata_creds
from utils.robonomics import transfer_xrt_2buy_subscription


# app = Quart(__name__)

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
STATUS_PAID_ID = os.getenv("ODOO_RRS_STATUS_PAID_ID")
STATUS_NOTPAID_ID = os.getenv("ODOO_RRS_STATUS_NOTPAID_ID")
ADMIN_SEED = os.getenv("ADMIN_SEED")
DONE_SATGE_ID = os.getenv("ODOO_HELPDESK_DONE_STAGE_ID")


class OdooView(Quart):
    def __init__(self, odoo, ws, name) -> None:
        super().__init__(name)
        self.odoo = odoo
        self.ws_client = ws
        self._logger = Logger("quart")
        self.route("/", methods=["GET"])(self.index)
        self.route("/rrs/payment", methods=["POST"])(self.payment_handler)

    def index(self):
        return "<h1>Welcome from Quart</h1>"

    async def payment_handler(self):
        request_data = await request.get_json()
        self._logger.debug(f"Data from payment request: {request_data}")
        print(asyncio.get_event_loop())
        if "status" in request_data.keys():
            status_id = int(request_data["status"])
            if status_id == int(STATUS_PAID_ID):
                id = int(request_data["id"])
                controller_address = request_data["address"]
                owner_address = str(request_data["owner_address"])
                pinata_keys = generate_pinata_keys(PINATA_API_KEY, PINATA_API_SECRET, owner_address)
                self.add_background_task(
                    self._odoo_request_add_pinata_creds, id, pinata_keys, controller_address, owner_address
                )
        return "Success"

    async def _odoo_request_add_pinata_creds(
        self, user_id: int, pinata_keys: dict, controller_address: str, owner_address: str
    ):
        pinata_key = pinata_keys["pinata_api_key"]
        pinata_secret = pinata_keys["pinata_api_secret"]
        print(f"is connected to the proxyfrom odoo 1 : {self.ws_client.libp2p_api.is_connected()}")
        self.odoo.update_rrs_user_with_pinata_creds(user_id, pinata_key, pinata_secret)
        msg = message_with_pinata_creds(pinata_key, pinata_secret, controller_address)
        protocol = f"/pinataCreds/{controller_address}"
        print(f"is connected to the proxyfrom odoo 2 : {self.ws_client.libp2p_api.is_connected()}")
        await self.ws_client.libp2p_api.send_msg_to_libp2p(msg, protocol, reconnect=True)
        try:
            transaction_hash = transfer_xrt_2buy_subscription(owner_address)
            if transaction_hash:
                self._logger.debug(f"XRT has been sent to ${owner_address}")
                self.odoo.update_rrs_user_with_subscription_status(user_id)
                await self.ws_client.libp2p_api.send_msg_to_libp2p(json.dumps(msg), protocol)
        except Exception as e:
            self._logger.error(f"Couldn't transfer XRT: {e}")
