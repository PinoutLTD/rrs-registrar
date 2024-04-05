from flask import Flask
import threading
import os
from dotenv import load_dotenv
from src.odoo import OdooProxy
from src.websocket import WSClient
from src.libp2p import wsClient
from src.quart_server import OdooView
from src.http_server import OdooFlaskView, BaseView

import asyncio

load_dotenv()

FLASK_PORT = os.getenv("FLASK_PORT")


def main() -> None:
    odoo = OdooProxy()
    # app = Flask(__name__)
    ws = wsClient(odoo)
    http_server = OdooView(odoo, ws, __name__)
    http_server.run(debug=True)

    # ws = WSClient(odoo)
    # BaseView.initialize(odoo, ws)
    # OdooFlaskView.register(app, route_base="/")
    # flask_thread = threading.Thread(target=lambda: app.run(host="127.0.0.1", port=FLASK_PORT))
    # flask_thread.start()
    # ws.run()
    # os._exit(0)


if __name__ == "__main__":
    main()
