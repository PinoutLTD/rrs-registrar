import os
import threading

from dotenv import load_dotenv
from flask import Flask

from registar.src.http_server import BaseView, OdooFlaskView
from registar.src.odoo import Odoo
from registar.src.websocket import WSClient

load_dotenv()
FLASK_PORT = os.getenv("FLASK_PORT")

class Registar:
    def __init__(self, add_user_callback, get_unpin_logs_from_IPFS_callback) -> None:
        self.odoo = Odoo()
        self.app = Flask(__name__)
        self.ws = WSClient(self.odoo)
        BaseView.initialize(add_user_callback, get_unpin_logs_from_IPFS_callback)
        OdooFlaskView.register(self.app, route_base="/")
        flask_thread = threading.Thread(target=lambda: self.app.run(host="127.0.0.1", port=FLASK_PORT))
        flask_thread.start()
        self.ws.run()
        os._exit(0)   