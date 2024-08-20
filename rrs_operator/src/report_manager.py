import json

from helpers.logger import Logger
from helpers.pinata import PinataHelper
from rrs_operator.utils.files_helper import FilesHelper
from rrs_operator.utils.ipfs_helper import IPFSHelper
from rrs_operator.utils.reports import ReportsFabric
from utils.decryption import decrypt_message

logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]
DESCRIPTION_FILE_NAME = "issue_description.json"

class ReportManager:
    def __init__(self, sender_public_key: str, report_msg: str) -> None:
        self._logger = Logger("report-manager")
        self.sender_public_key = sender_public_key
        self.report_msg = report_msg
        self._temp_dir = FilesHelper.create_temp_directory()
        self.ipfs = IPFSHelper()
    
    def get_description_and_priority(self) -> tuple:
        with open(f"{self._temp_dir}/{DESCRIPTION_FILE_NAME}") as f:
            issue = json.load(f)
            if isinstance(issue['description'], dict):
                description_type = issue["description"]["type"]
                unparsed_description = issue["description"]["description"]
            else:
                description_type = "errors"
                unparsed_description = issue["description"]
            report = ReportsFabric.get_report(description_type)
            description = report.get_descriptions(unparsed_description)
            priority = report.get_priority()
        FilesHelper.remove_directory(self._temp_dir)
        return description, priority  

    def get_logs_hashes(self) -> list:
        return self.ipfs.logs_hashes

    def process_report(self):
        report_msg_type = self._defind_type_of_report_message()
        if report_msg_type == "json":
            self._handle_json_report()
        else:
            self._handle_str_report()

    def _defind_type_of_report_message(self):
        try:
            json.loads(self.report_msg)
            return "json"
        except json.decoder.JSONDecodeError:
            return "str"
    
    def _handle_json_report(self):
        self._logger.debug("Handling json report.")
        dict_with_logs = json.loads(self.report_msg)
        for k, v in dict_with_logs.items():
            encrypted_content = PinataHelper.download_file(hash=v, logger=self._logger)
            path_to_saved_file = self._save_decrypted_logs(encrypted_content=encrypted_content, file_name=k)
            if k == DESCRIPTION_FILE_NAME:
                self._logger.debug("Unppining description file from Pinata...")
                PinataHelper.unpin_file(hash=v, logger=self._logger)
            else:
                self._logger.debug(f"Pinning file {path_to_saved_file} to the IPFS node...")
                self.ipfs.pin_file(path_to_saved_file)

    def _handle_str_report(self):
        self._logger.debug("Handling string report.")
        for log in logs_name:
            encrypted_content = PinataHelper.download_file_from_directory(hash=self.report_msg, logger=self._logger, file_name=log)
            path_to_saved_file = self._save_decrypted_logs(encrypted_content=encrypted_content, file_name=log)
            if not(log == DESCRIPTION_FILE_NAME):
                self._logger.debug(f"Pinning file {path_to_saved_file} to the IPFS node...")
                self.ipfs.pin_file(path_to_saved_file)
    
    def _save_decrypted_logs(self, encrypted_content: str, file_name: str):
        decrypted_content = decrypt_message(encrypted_content, self.sender_public_key, self._logger)
        path_to_saved_file = FilesHelper.create_and_save_file(decrypted_content, self._temp_dir, file_name)
        return path_to_saved_file

    