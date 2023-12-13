import robonomicsinterface as ri
from robonomicsinterface.utils import ipfs_32_bytes_to_qm_hash
import typing as tp
from dotenv import load_dotenv
import threading
import os

from src.ipfs import IPFSHelpder
from utils.logger import Logger

load_dotenv()

ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")
WSS_ENDPOINT = os.getenv("WSS_ENDPOINT")


class RobonomicsHelper:
    def __init__(self, odoo) -> None:
        self.account = ri.Account(remote_ws=WSS_ENDPOINT)
        self._logger = Logger("robonomics")
        self.odoo = odoo

    def subscribe(self) -> ri.Subscriber:
        """Subscribe to the NewLaunch event"""

        self._logger.debug("Susbcribed to NewLaunch event")
        self.subscriber = ri.Subscriber(
            self.account,
            ri.SubEvent.NewLaunch,
            subscription_handler=self._on_new_launch,
        )
        self._is_subscription_alive()

    def _on_new_launch(self, data: tp.Tuple[tp.Union[str, tp.List[str]]]) -> None:
        """NewLaunch callback

        :param data: Data from the launch
        """

        try:
            if data[1] == ADMIN_ADDRESS:
                hash = ipfs_32_bytes_to_qm_hash(data[2])
                self._logger.info(f"Robonomics:  Ipfs hash: {hash}")
                robonomics_address_from = data[0]
                threading.Thread(
                    target=self._handle_data,
                    args=(
                        hash,
                        robonomics_address_from,
                    ),
                ).start()

        except Exception as e:
            self._logger.error(f"Problem in on new launch: {e}")

    def _handle_data(self, ipfs_hash: str, robonomics_address_from: str) -> None:
        """Handle data from the launch: create ticket and add logs

        :param robonomics_address_from: User's address in Robonomics parachain
        """

        ipfs = IPFSHelpder(robonomics_address_from)
        email, phone, description = ipfs.parse_logs(ipfs_hash)
        self._logger.debug(f"Data from ipfs: {email}, {phone}, {description}")
        ticket_id = self.odoo.create_ticket(email, robonomics_address_from, phone, description)
        if len(os.listdir(ipfs.temp_dir)) > 1:
            for f in os.listdir(ipfs.temp_dir):
                if f == "issue_description.json":
                    pass
                else:
                    file_name = f
                    file_path = f"{ipfs.temp_dir}/{f}"
                    self.odoo.create_note_with_attachment(ticket_id, file_name, file_path)
        ipfs.clean_temp_dir()

    def _resubscribe(self) -> None:
        """Close the subscription and create a new one"""

        self._logger.debug("Resubscribe")
        self.subscriber.cancel()
        self.subscribe()

    def _is_subscription_alive(self) -> None:
        """Ckeck every 15 sec if subscription is alive"""

        threading.Timer(
            15,
            self._is_subscription_alive,
        ).start()
        if self.subscriber._subscription.is_alive():
            return
        self._resubscribe()
