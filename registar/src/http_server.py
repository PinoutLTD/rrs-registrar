from flask import request
from flask_classful import FlaskView, route
from dotenv import load_dotenv
import os

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
    def initialize(cls, add_user_callback):
        cls.set_logger()
        cls.add_user_callback = add_user_callback

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