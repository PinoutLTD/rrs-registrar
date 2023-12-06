import websocket
import os
from dotenv import load_dotenv
import json
from utils.logger import logger
from utils.decrypt_msg import decrypt_message

load_dotenv()

LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")
ADMIN_SEED = os.getenv("ADMIN_SEED")


class WSClient:
    def __init__(self, odoo) -> None:
        self._logger = logger("websocket")
        self.odoo = odoo
        self.ws = self._connect2server()
        self.ws.run_forever()
        

    def _connect2server(self):
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            LIBP2P_WS_SERVER,
            on_open=self._on_connection,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        return ws

    def _on_connection(self, ws):
        self._logger.DEBUG(f"Websocket: Connceted to {LIBP2P_WS_SERVER}")
        self.ws.send(json.dumps({"protocols_to_listen": ["/initialization"]} ))

    def _on_message(self, ws, message):
        json_message = json.loads(message)
        self._logger.DEBUG(f"Websocket: Got msg: {json_message}")
        if not "email" in json_message:
            decrypted_email = json_message["email"]
            robonomics_address = json_message["address"]
            encrypted_email = decrypt_message(decrypted_email, robonomics_address, ADMIN_SEED)
            self.odoo.create_rrs_user(encrypted_email, robonomics_address)

    def _on_error(self, ws, error):
        self._logger.WARNING(f"Websocket: Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.DEBUG(f"Websocket: Connection closed with status code {close_status_code} and message {close_msg}")
