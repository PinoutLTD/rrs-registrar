from flask import Flask
import threading

from src.robonomics import RobonomicsHelper
from src.odoo import OdooProxy
from src.websocket import WSClient
from src.http_server import OdooFlaskView, BaseView


def main() -> None:
    odoo = OdooProxy()
    app = Flask(__name__)
    ws = WSClient(odoo)
    BaseView.initialize(odoo, ws)
    OdooFlaskView.register(app, route_base="/")
    threading.Thread(target=lambda: app.run(host="127.0.0.1", port=5000)).start()
    robonomics = RobonomicsHelper(odoo)
    robonomics.subscribe()


if __name__ == "__main__":
    main()
