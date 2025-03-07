import os
import threading
import typing as tp

import robonomicsinterface as ri
from dotenv import load_dotenv

from helpers.logger import Logger

load_dotenv()

ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")
WSS_ENDPOINT = os.getenv("WSS_ENDPOINT")


class RobonomicsHelper:
    def __init__(self, odoo) -> None:
        self.account = ri.Account(remote_ws=WSS_ENDPOINT)
        self.rws = ri.RWS(self.account)
        self._logger = Logger("robonomics")
        self.odoo = odoo
        self.users = self.rws.get_devices(ADMIN_ADDRESS)
        self._track_free_weight()
    
    def add_user_callback(self, address: str) -> None:
        """Updates the list of users to track new datalogs for
        :param address: Address to add
        """
        self.users.append(address)

    def subscribe(self) -> ri.Subscriber:
        """Subscribe to the NewRecord event"""

        self._logger.debug("Susbcribed to NewRecord event")
        self.subscriber = ri.Subscriber(
            self.account,
            ri.SubEvent.NewRecord,
            subscription_handler=self._on_new_record,
        )
        self._is_subscription_alive()

    def _on_new_record(self, data: tp.Tuple[tp.Union[str, tp.List[str]]]) -> None:
        """NewRecord callback

        :param data: Data from the launch
        """
        pass

        # try:
        #     if data[0] in self.users:
        #         hash = data[2]
        #         self._logger.info(f"Ipfs hash: {hash}")
        #         robonomics_address_from = data[0]
        #         threading.Thread(
        #             target=self._handle_data,
        #             args=(
        #                 hash,
        #                 robonomics_address_from,
        #             ),
        #         ).start()

        # except Exception as e:
        #     self._logger.error(f"Problem in on new record: {e}")

    def _handle_data(self, report_msg: str, robonomics_address_from: str) -> None:
        """Handle data from the datalog: create ticket and add logs

        :param robonomics_address_from: User's address in Robonomics parachain
        """
        pass
        # report_manager = ReportManager(robonomics_address_from, report_msg)
        # report_manager.process_report()
        # email = self.odoo.find_user_email(robonomics_address_from)
        # descriptions_list, priority = report_manager.get_description_and_priority()
        # logs_hashes = report_manager.get_logs_hashes()
        # self._logger.debug(f"Data from ipfs: {email}, {descriptions_list}, priority: {priority}")
        # for description in descriptions_list:
        #     ticket_id = self.odoo.find_ticket_with_description(description, email)
        #     if not ticket_id:
        #         ticket_id = self.odoo.create_ticket(email, robonomics_address_from, description, priority)
            
        #     if logs_hashes:
        #         for hash in logs_hashes:
        #             self.odoo.create_note_with_logs_hash(ticket_id, hash)


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

    def _track_free_weight(self) -> None:
        """Track free weight of the subscription"""
        threading.Timer(60, self._track_free_weight,).start()
        free_weight = self.rws.get_ledger(ADMIN_ADDRESS)
        self._logger.debug(f"Free weight in subscription: {free_weight}")

