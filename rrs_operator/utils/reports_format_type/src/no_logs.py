import json

from .report import Report
from helpers.logger import Logger

class NoLogs(Report):
    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger

    def handle_report(self, report_msg: str, sender_address: str, temp_dir: str):
        self._logger.debug("Handling no-logs report.")
        encrypted_description = json.loads(report_msg)[self.DESCRIPTION_FILE_NAME]
        path_to_saved_file = self.save_decrypted_logs(encrypted_content=encrypted_description, file_name=self.DESCRIPTION_FILE_NAME, sender_address=sender_address, temp_dir=temp_dir   )
