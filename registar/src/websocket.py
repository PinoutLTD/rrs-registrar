import json
import os

import rel
import websocket
from dotenv import load_dotenv

from helpers.logger import Logger
from helpers.pinata import PinataHelper
from registar.utils.messages import (message_for_subscribing,
                                     message_with_pinata_creds, 
                                     message_with_robonomics_address)
from registar.utils.robonomics import add_device_to_subscription
from registar.utils.message_manager import MessageManager
from utils.decryption import decrypt_message

load_dotenv()

LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")
ADMIN_SEED = os.getenv("ADMIN_SEED")
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

PAID_SERVICE = False


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
        message_manager = MessageManager(self.odoo)
        msg = message_manager.select_formatter(message_data)
        self.ws.send(msg)

    def _on_error(self, ws, error):
        self._logger.error(f"{error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.debug(f"Connection closed with status code {close_status_code} and message {close_msg}")