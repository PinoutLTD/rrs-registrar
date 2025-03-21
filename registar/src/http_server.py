from flask import request, Response, jsonify
from flask_classful import FlaskView, route
from dotenv import load_dotenv
import os
import threading
import requests

from helpers.logger import Logger
from registar.utils.odoo_requests import save_cid_and_orderid, save_orderid, update_last_paid, set_status_not_paid, setup_new_paid_customer
from registar.utils.jwt import jwt_required, generate_token

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
STATUS_PAID_ID = os.getenv("ODOO_RRS_STATUS_PAID_ID")
STATUS_NOTPAID_ID = os.getenv("ODOO_RRS_STATUS_NOTPAID_ID")
ADMIN_SEED = os.getenv("ADMIN_SEED")
DONE_SATGE_ID = os.getenv("ODOO_HELPDESK_DONE_STAGE_ID")
PAYMENT_PROVIDER_URL = os.getenv("PAYMENT_PROVIDER_URL")


class BaseView(FlaskView):
    odoo = None
    ws = None
    _logger = None

    @classmethod
    def initialize(cls, add_user_callback, unpin_logs_from_IPFS_callback, get_file_from_IPFS_callback, odoo):
        cls.set_logger()
        cls.odoo = odoo
        cls.add_user_callback = add_user_callback
        cls.unpin_logs_from_IPFS_callback = unpin_logs_from_IPFS_callback
        cls.get_file_from_IPFS_callback = get_file_from_IPFS_callback

    @classmethod
    def set_logger(cls):
        cls._logger = Logger("flask")

class OdooFlaskView(BaseView):
    def index(self):
        return "<h1>Welcome from Flask</h1>"

    @route("/odoo/new-user", methods=["POST"])
    def new_user_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from new-user request: {request_data}")
        address = request_data["address"]
        self.add_user_callback(address)
        return "ok"

    @route("/odoo/ticket-done", methods=["POST"])
    def ticket_dont_handler(self):
        request_data = request.get_json()
        self._logger.debug(f"Data from ticket-done request: {request_data}")
        if int(request_data["stage"]) == int(DONE_SATGE_ID):
            ticket_id = int(request_data["id"])
            self.unpin_logs_from_IPFS_callback(ticket_id)
        return "ok"
    
    @route("/odoo/ipfs/<hash>", methods=["GET"])
    def download_logs_handler(self, hash):
        log_content = self.get_file_from_IPFS_callback(hash)
        response = Response(log_content)
        response.headers["Content-Disposition"] = f"attachment; filename={hash}"
        response.headers["Content-Type"] = "text/plain"
        return response

    @route("/odoo/next-payment/<cid>", methods=["POST"])
    def next_payment_handler(self, cid):
        request_data = request.get_json()
        self._logger.debug(f"Data from next-payment request: {request_data}")
        paid = request_data.get("paid")
        if not paid:
            return
        threading.Thread(target=self._prolongation_request, args=(cid,)).start()
        return Response(status=200)
    
    def _prolongation_request(self, cid: str):
        data = {"cid": cid}
        token = generate_token()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.post(url=f"{PAYMENT_PROVIDER_URL}/prs/prolongation", json=data, headers=headers)
    
    @route("/paymentProvider/saveCustomerData/<email>", methods=["PUT"])
    @jwt_required
    def save_customer_data_handler(self, email):
        request_data = request.get_json()
        self._logger.debug(f"Data from save_customer_data request: {request_data}")
        cid = request_data.get("cid")
        order_id = request_data.get("order_id")
        if not cid or not order_id:
            return jsonify({"error": "Both 'cid' and 'order_id' are required"}), 400
        threading.Thread(target=save_cid_and_orderid, args=(self.odoo,cid, order_id, email,)).start()
        return Response(status=200)
    
    @route("/paymentProvider/updateOrderId/<cid>", methods=["PUT"])
    @jwt_required
    def update_orderid_handler(self, cid):
        request_data = request.get_json()
        order_id = request_data.get("order_id")
        if not order_id:
            return jsonify({"error": "Order_id is required"}), 400
        save_orderid(self.odoo, cid, order_id)
        self._logger.debug("/updateOrderId: order id updated")
        return Response(status=200)
    
    @route("/paymentProvider/updateLastPaid", methods=["POST"])
    @jwt_required
    def update_last_paid_handler(self):
        """Webhook for Revolut successful payment"""
        request_data = request.get_json()
        self._logger.debug(f"Data from revolut webhook request: {request_data}")
        order_id = request_data.get("order_id")
        if not order_id:
            return jsonify({"error": "Order_id is required"}), 400
        thread1 = threading.Thread(target=setup_new_paid_customer, args=(self.odoo, order_id,self.unpin_logs_from_IPFS_callback))
        thread1.start()
        thread1.join(timeout=10)
        threading.Thread(target=update_last_paid, args=(self.odoo, order_id,)).start()
        return Response(status=200)

    @route("/paymentProvider/setUnpaid", methods=["POST"])
    @jwt_required
    def payment_failed_handler(self):
        """Webhook for Revolut failed payment"""
        request_data = request.get_json()
        self._logger.debug(f"Data from revolut webhook request: {request_data}")
        order_id = request_data.get("order_id")
        if not order_id:
            return jsonify({"error": "Order_id is required"}), 400
        threading.Thread(target=set_status_not_paid, args=(self.odoo, order_id,)).start()
        return Response(status=200)
