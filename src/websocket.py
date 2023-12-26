import websocket
import os
from dotenv import load_dotenv
import json
import rel
from utils.logger import Logger
from utils.decrypt_encrypt_msg import decrypt_message

load_dotenv()

LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")
ADMIN_SEED = os.getenv("ADMIN_SEED")


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
        self.ws.send(json.dumps({"protocols_to_listen": ["/initialization"]}))

    def _on_message(self, ws, message):
        json_message = json.loads(message)
        self._logger.debug(f"Got msg: {json_message}")
        if "email" in json_message:
            decrypted_email = json_message["email"]
            owner_address = json_message["owner_address"]
            controller_address = json_message["controller_address"]
            encrypted_email = decrypt_message(decrypted_email, controller_address, ADMIN_SEED)
            self.odoo.create_rrs_user(encrypted_email, owner_address, controller_address)
            self.odoo.create_invoice(owner_address, encrypted_email)

    def _on_error(self, ws, error):
        self._logger.error(f"{error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.debug(f"Connection closed with status code {close_status_code} and message {close_msg}")
