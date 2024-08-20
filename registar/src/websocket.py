import websocket
import os
from dotenv import load_dotenv
import json
import rel
from helpers.logger import Logger
from utils.decryption import decrypt_message
from registar.utils.messages import message_with_pinata_creds, message_for_subscribing
from registar.utils.robonomics import add_device_to_subscription
from helpers.pinata import PinataHelper

load_dotenv()

LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")
ADMIN_SEED = os.getenv("ADMIN_SEED")
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")


class WSClient:
    def __init__(self, odoo) -> None:
        self.odoo = odoo
        self._logger = Logger("websocket")
        self._connect2server()

    def _connect2server(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            url=LIBP2P_WS_SERVER,
            on_open=self._on_connection,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

    def run(self) -> None:
        self.ws.run_forever(dispatcher=rel, reconnect=5)
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()

    def _on_connection(self, ws):
        self._logger.debug(f"Connected to {LIBP2P_WS_SERVER}")
        msg = message_for_subscribing()
        self._logger.debug(f"Connection msg: {msg}")
        self.ws.send(msg)

    def _on_message(self, ws, message):
        json_message = json.loads(message)
        self._logger.debug(f"Got msg: {json_message}")
        if "peerId" in json_message:
            return
        message_data = json_message["data"]
        if "email" in message_data:
            encrypted_email = message_data["email"]
            sender_address = message_data["sender_address"]
            decrypted_email = decrypt_message(encrypted_email, sender_address, self._logger)
            rrs_user_id = self.odoo.check_if_rrs_user_exists(sender_address)
            if rrs_user_id:
                pinata_key, pinata_secret = self.odoo.retrieve_pinata_creds(sender_address, rrs_user_id)
                if pinata_key:
                    msg = message_with_pinata_creds(pinata_key, pinata_secret, sender_address, self._logger)
                    self.ws.send(msg)
                    return
            user_id = self.odoo.create_rrs_user(decrypted_email, sender_address)
            hash = add_device_to_subscription(sender_address)
            if hash:
                self._logger.debug(f"Add {sender_address} to subscription")
                pinata_keys = PinataHelper.generate_pinata_keys(sender_address)
                pinata_key = pinata_keys["pinata_api_key"]
                pinata_secret = pinata_keys["pinata_api_secret"]
                self._logger.debug(f"Pinata creds: {pinata_key}, {pinata_secret}, {pinata_keys}")
                self.odoo.update_rrs_user_with_pinata_creds(user_id, pinata_key, pinata_secret)
                msg = message_with_pinata_creds(pinata_key, pinata_secret, sender_address, self._logger)
                self.ws.send(msg)

            else:
                self._logger.error(f"Couldn't add {sender_address} to subscription: {hash}")

    def _on_error(self, ws, error):
        self._logger.error(f"{error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.debug(f"Connection closed with status code {close_status_code} and message {close_msg}")


