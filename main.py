from src.robonomics import RobonomicsHelper
from src.odoo import OdooHelper


odoo = OdooHelper()
robonomics = RobonomicsHelper(odoo)


def main() -> None:
    robonomics.subscribe()


if __name__ == "__main__":
    main()
