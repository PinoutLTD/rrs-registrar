import json

from helpers.logger import Logger
from rrs_operator.utils.files_helper import FilesHelper
from rrs_operator.utils.ipfs_helper import IPFSHelper
from rrs_operator.utils.reports_problem_type import ReportsProblemTypeFabric
from rrs_operator.utils.reports_format_type import ReportsFormatTypeFabric

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
            report = ReportsProblemTypeFabric.get_report(description_type)
            description = report.get_descriptions(unparsed_description)
            priority = report.get_priority()
        FilesHelper.remove_directory(self._temp_dir)
        return description, priority  

    def get_logs_hashes(self) -> list:
        return self.ipfs.logs_hashes

    def process_report(self):
        report = ReportsFormatTypeFabric.get_report(report_msg=self.report_msg, logger=self._logger, ipfs=self.ipfs)
        report.handle_report(self.report_msg, self.sender_address, self._temp_dir)