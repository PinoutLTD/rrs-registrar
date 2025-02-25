import json
from helpers.logger import Logger
from rrs_operator.utils.files_helper import FilesHelper
from rrs_operator.utils.ipfs_helper import IPFSHelper
from helpers.pinata import PinataHelper
from rrs_operator.utils.hash_cash import HashCache
from rrs_operator.utils.messages import  message_report_response
from rrs_operator.utils.ticket_manager import TicketManager
from rrs_operator.utils.reports_problem_type import ReportsProblemTypeFabric
from rrs_operator.utils.reports_format_type import ReportsFormatTypeFabric

DESCRIPTION_FILE_NAME = "issue_description.json"

class MessageProcessor:
    def __init__(self, odoo) -> None:
        self._logger = Logger("message-processor")
        self.ipfs = IPFSHelper()
        self.odoo = odoo
        self._temp_dir = FilesHelper.create_temp_directory()

    def process_message(self, message) -> None | str:
        json_message = json.loads(message)
        self._logger.debug(f"Got msg: {json_message}")

        if "peerId" in json_message:
            return

        message_data = json_message.get("data", {})
        if "report" not in message_data:
            return

        sender_address = message_data.get("address")
        json_report_message = json.dumps(message_data["report"])
        email = self.odoo.find_user_email(sender_address)

        if not email:
            self._logger.debug(f"Address {sender_address} is not registered in Odoo.")
            return

        # **1. Determine Report Type**
        report_type = ReportsFormatTypeFabric.get_report(json_report_message, self.ipfs, self._logger)
        report_type.handle_report(json_report_message, sender_address, self._temp_dir)

        # **2. Determine Problem Type**
        issue = self._get_issue()
        problem_handler = ReportsProblemTypeFabric.get_report(issue)
        descriptions_list = problem_handler.get_descriptions()
        priority = problem_handler.get_priority()
        source = issue["description"].get("source", "")
        FilesHelper.remove_directory(self._temp_dir)

        # **3. Ticket Management**
        ticket_manager = TicketManager(self.odoo)
        logs_hashes = self.ipfs.logs_hashes
        ticket_ids, is_paid = ticket_manager.process_ticket(descriptions_list, priority, source, email, sender_address, logs_hashes)

        # **4. Handle Unpinning for Free Users**
        if not is_paid:
            free_hashes = HashCache.get_hashes(sender_address)
            for hash in free_hashes:
                PinataHelper.unpin_file(hash, self._logger)
        return message_report_response(datalog=is_paid, ticket_ids=ticket_ids, sender_address=sender_address)


    def _get_issue(self) -> dict:
        with open(f"{self._temp_dir}/{DESCRIPTION_FILE_NAME}") as f:
            return json.load(f)