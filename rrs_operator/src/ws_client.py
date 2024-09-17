import json
import os

import websocket
from dotenv import load_dotenv

from helpers.logger import Logger
from rrs_operator.src.report_manager import ReportManager
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
        json_message = json.loads(message)
        self._logger.debug(f"Got msg: {json_message}")
        if "peerId" in json_message:
            return
        message_data = json_message["data"]
        if "report" in message_data:
            sender_address = message_data["address"]
            json_report_message = json.dumps(message_data["report"])
            email = self.odoo.find_user_email(sender_address)
            if email:
                report_manager = ReportManager(sender_address, json_report_message)
                report_manager.process_report()
                descriptions_list, priority, source = report_manager.get_description_and_priority()
                logs_hashes = report_manager.get_logs_hashes()
                self._logger.debug(f"Data from ipfs: {email}, {descriptions_list}, priority: {priority}, source: {source}")
                for description in descriptions_list:
                    if (source == "devices") or (source == ""):
                        ticket_id = self.odoo.find_ticket_with_description(description, email)
                    else:
                        ticket_id = self.odoo.find_ticket_with_source(source, email)
                    if ticket_id:
                        self.odoo.get_and_increase_problem_counter(ticket_id)
                    else:
                        ticket_id = self.odoo.create_ticket(email, sender_address, description, priority, source)
                
                    if logs_hashes:
                        for hash in logs_hashes:
                            self.odoo.create_note_with_logs_hash(ticket_id, hash)
            else:
                self._logger.debug(f"Address {sender_address} is not registred in Odoo. Email is: {email}")


    def _on_error(self, ws, error):
        self._logger.error(f"{error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self._logger.debug(f"Connection closed with status code {close_status_code} and message {close_msg}")
