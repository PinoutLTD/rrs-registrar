import robonomicsinterface as ri
from dotenv import load_dotenv
import os
import typing as tp
from robonomicsinterface.utils import ipfs_32_bytes_to_qm_hash
import threading

from ipfs import IPFSHelpder
from odoo import OdooHelper
from utils.logger import logger

load_dotenv()

ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")
WSS_ENDPOINT = os.getenv("WSS_ENDPOINT")


odoo = OdooHelper()

_logger = logger("helpdesk")


def _is_subscription_alive(subscriber) -> None:
    threading.Timer(15, _is_subscription_alive, [subscriber]).start()
    if subscriber._subscription.is_alive():
        return
    _resubscribe(subscriber)


def _resubscribe(subscriber) -> None:
    """Close the subscription and create a new" one"""
    print("resubscribe")
    subscriber.cancel()
    subscribe()

def _handle_data(ipfs_hash: str, robonomics_address_from: str) -> None:
    ipfs = IPFSHelpder()
    _logger.debug(f"Thread in handle data: {threading.current_thread()}")
    email, phone, description = ipfs.parse_logs(ipfs_hash)
    _logger.debug(f"Data from ipfs: {email}, {phone}, {description}")
    ticket_id = odoo.create_ticket(email, robonomics_address_from, phone, description)
    _logger.info(f"Ticket id: {ticket_id}")
    if len(os.listdir(ipfs.temp_dir)) > 1:
        for f in os.listdir(ipfs.temp_dir):
            if f == "issue_description.json":
                pass
            else:
                file_name = f
                file_path = f"{ipfs.temp_dir}/{f}"
                odoo.create_note_with_attachment(ticket_id, file_name, file_path)
    ipfs.clean_temp_dir()


def _on_new_launch(data: tp.Tuple[tp.Union[str, tp.List[str]]]) -> None:
    """NewLaunch callback

    :param data: Data from the launch
    """
    try:
        print(data)
        _logger.debug(f"Thread in callback: {threading.current_thread()}")
        if data[1] == ADMIN_ADDRESS:
            hash = ipfs_32_bytes_to_qm_hash(data[2])
            _logger.info(f"Ipfs hash: {hash}")
            robonomics_address_from = data[0]
            threading.Thread(target=_handle_data, args=(hash, robonomics_address_from,)).start()
            for thread in threading.enumerate(): 
                print(thread.name)


    except Exception as e:
        _logger.warning(f"Problem in on new launch: {e}")


def subscribe() -> ri.Subscriber:
    _logger.debug(f"Thread in subscriber: {threading.current_thread()}")
    account = ri.Account(remote_ws=WSS_ENDPOINT)
    _logger.debug("Susbcribed to NewLaunch event")
    subscriber = ri.Subscriber(
        account,
        ri.SubEvent.NewLaunch,
        subscription_handler=_on_new_launch,
    )
    _is_subscription_alive(subscriber)


def main() -> None:
    subscribe()


if __name__ == "__main__":
    main()
