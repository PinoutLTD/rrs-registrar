from abc import ABC, abstractmethod
from utils.decryption import decrypt_message
from rrs_operator.utils.files_helper import FilesHelper


class Report(ABC):
    def __init__(self) -> None:
        self.DESCRIPTION_FILE_NAME = "issue_description.json"

    @abstractmethod
    def handle_report(self, report_msg: str) -> None:
        pass

    def save_decrypted_logs(self, encrypted_content: str, file_name: str, sender_address: str, temp_dir: str):
        decrypted_content = decrypt_message(encrypted_content, sender_address, self._logger)
        path_to_saved_file = FilesHelper.create_and_save_file(decrypted_content, temp_dir, file_name)
        return path_to_saved_file
