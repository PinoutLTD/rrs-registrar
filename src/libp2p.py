from utils.decrypt_encrypt_msg import decrypt_message
import os
from dotenv import load_dotenv
import asyncio
from pyproxy import Libp2pProxyAPI
from utils.logger import Logger
from utils.messages import message_with_pinata_creds

load_dotenv()

ADMIN_SEED = os.getenv("ADMIN_SEED")
LIBP2P_WS_SERVER = os.getenv("LIBP2P_WS_SERVER")


class wsClient:
    def __init__(self, odoo) -> None:
        self.odoo = odoo
        self._logger = Logger("websocket")
        self._logger.debug("ws")
        self.libp2p_api = Libp2pProxyAPI(LIBP2P_WS_SERVER)
        asyncio.run(self.libp2p_api.subscribe_to_protocol_sync("/initialization", self.on_initialization_msg, reconnect=False))
        print(f"is connected to the proxy: {self.libp2p_api.is_connected()}")


    def on_initialization_msg(self, msg: dict) -> None:
        self._logger.debug(f"Got msg: {msg}")
        if "email" in msg:
            decrypted_email = msg["email"]
            owner_address = msg["owner_address"]
            controller_address = msg["controller_address"]
            encrypted_email = decrypt_message(decrypted_email, controller_address, ADMIN_SEED)
            rrs_user_id = self.odoo.check_if_rrs_user_exists(controller_address)
            if rrs_user_id:
                pinata_key, pinata_secret = self.odoo.retrieve_pinata_creds(controller_address, rrs_user_id)
                if pinata_key:
                    msg = message_with_pinata_creds(pinata_key, pinata_secret, controller_address)
                    self.ws.send(msg)
                    return
                else:
                    is_invoice_posted = self.odoo.check_if_invoice_posted(owner_address)
                    if is_invoice_posted:
                        return
            self._logger.error(f"Couldn't get pinata creds. Creating a new one..")
            self.odoo.create_rrs_user(encrypted_email, owner_address, controller_address)
            self.odoo.create_invoice(owner_address, encrypted_email)