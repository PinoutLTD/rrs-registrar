import os

from dotenv import load_dotenv
from flask import Response, request
from flask_classful import FlaskView, route

from helpers.logger import Logger

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
    def initialize(cls, add_user_callback, unpin_logs_from_IPFS_callback, get_file_from_IPFS_callback):
        cls.set_logger()
        cls.add_user_callback = add_user_callback
        cls.unpin_logs_from_IPFS_callback = unpin_logs_from_IPFS_callback
        cls.get_file_from_IPFS_callback = get_file_from_IPFS_callback

    @classmethod
    def set_logger(cls):
        cls._logger = Logger("flask")


class OdooFlaskView(BaseView):
    def index(self):
        return "<h1>Welcome from Flask</h1>"

    @route("/rrs/new-user", methods=["POST"])
    def new_user_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from new-user request: {request_data}")
        address = request_data["address"]
        self.add_user_callback(address)
        return "ok"

    @route("/rrs/ticket-done", methods=["POST"])
    def ticket_dont_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from ticket-done request: {request_data}")
        if int(request_data["stage"]) == int(DONE_SATGE_ID):
            ticket_id = int(request_data["id"])
            self.unpin_logs_from_IPFS_callback(ticket_id)
        return "ok"
    
    @route("/rrs/ipfs/<hash>", methods=["GET"])
    def download_logs_handler(self, hash):
        log_content = self.get_file_from_IPFS_callback(hash)
        response = Response(log_content)
        response.headers["Content-Disposition"] = f"attachment; filename={hash}"
        response.headers["Content-Type"] = "text/plain"
        return response

