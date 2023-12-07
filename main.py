from src.robonomics import RobonomicsHelper
from src.odoo import OdooHelper
from src.websocket import WSClient



def main() -> None:
    odoo = OdooHelper()
    ws = WSClient(odoo)
    robonomics = RobonomicsHelper(odoo)
    robonomics.subscribe()


if __name__ == "__main__":
    main()
