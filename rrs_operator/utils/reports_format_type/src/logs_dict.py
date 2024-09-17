from tenacity import *
import json

from .report import Report
from helpers.logger import Logger
from helpers.pinata import PinataHelper

class LogsDict(Report):
    def __init__(self, logger: Logger, ipfs):
        super().__init__()
        self._logger = logger
        self.ipfs = ipfs

    @retry(wait=wait_fixed(10))
    def handle_report(self, report_msg: str, sender_address: str, temp_dir: str):
        self._logger.debug("Handling logs-dict report.")
        try:
            dict_with_logs = json.loads(report_msg)
            for k, v in dict_with_logs.items():
                encrypted_content = PinataHelper.download_file(hash=v, logger=self._logger)
                path_to_saved_file = self.save_decrypted_logs(encrypted_content=encrypted_content, file_name=k, sender_address=sender_address, temp_dir=temp_dir)
                # if not(k == DESCRIPTION_FILE_NAME):
                self._logger.debug("Unppining logs file from Pinata...")
                PinataHelper.unpin_file(hash=v, logger=self._logger)
                if not(k == self.DESCRIPTION_FILE_NAME):
                    self._logger.debug(f"Pinning file {path_to_saved_file} to the IPFS node...")
                    self.ipfs.pin_file(path_to_saved_file)
        except Exception as e:
            self._logger.error(f"Error while handling json report: {e}")
            raise e
