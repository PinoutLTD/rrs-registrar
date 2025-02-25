import os

import websocket
from dotenv import load_dotenv

from helpers.logger import Logger
from .message_processor import MessageProcessor
from rrs_operator.utils.messages import message_for_subscribing

load_dotenv()

LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")
ADMIN_SEED = os.getenv("ADMIN_SEED")

class WSClient:
    def __init__(self, odoo) -> None:
        self.odoo = odoo
        self._logger = Logger("operator-ws")
        self._connect2server()

    def _connect2server(self):
        self.ws = websocket.WebSocketApp(
            url=LIBP2P_WS_SERVER,
            on_open=self._on_connection,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

    def run(self) -> None:
        self.ws.run_forever(reconnect=5)

    def _on_connection(self, ws):
        self._logger.debug(f"Connected to {LIBP2P_WS_SERVER}")
        msg = message_for_subscribing()
        self._logger.debug(f"Connection msg: {msg}")
        self.ws.send(msg)

    def _on_message(self, ws, message):
        msg_processor = MessageProcessor(self.odoo)
        reponse = msg_processor.process_message(message)
        self.ws.send(reponse)

    def _on_error(self, ws, error):
        self._logger.error(f"{error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.debug(f"Connection closed with status code {close_status_code} and message {close_msg}")
