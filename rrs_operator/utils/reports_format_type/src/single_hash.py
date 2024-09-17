from tenacity import *

from .report import Report
from helpers.logger import Logger
from helpers.pinata import PinataHelper

logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]

class SingleHash(Report):
    def __init__(self, logger: Logger, ipfs):
        super().__init__()
        self._logger = logger
        self.ipfs = ipfs

    @retry(wait=wait_fixed(10))
    def handle_report(self, report_msg: str, sender_address: str, temp_dir: str):
        self._logger.debug("Handling single hash report.")
        for log in logs_name:
            encrypted_content = PinataHelper.download_file_from_directory(hash=report_msg, logger=self._logger, file_name=log)
            path_to_saved_file = self.save_decrypted_logs(encrypted_content=encrypted_content, file_name=log, sender_address=sender_address, temp_dir=temp_dir)
            if not(log == self.DESCRIPTION_FILE_NAME):
                self._logger.debug(f"Pinning file {path_to_saved_file} to the IPFS node...")
                self.ipfs.pin_file(path_to_saved_file)
