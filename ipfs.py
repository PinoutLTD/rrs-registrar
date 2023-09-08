import tempfile
import json
from dotenv import load_dotenv
import requests
import shutil
import threading
import os
from utils.logger import logger
from utils.decrypt_msg import decrypt_message

load_dotenv()

_logger = logger("ipfs")
logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]

ADMIN_SEED = os.getenv("ADMIN_SEED")


class IPFSHelpder:
    def __init__(self, sender_public_key: str) -> None:
        self.sender_public_key = sender_public_key
        self.temp_dir = tempfile.mkdtemp()

    def _download_file(self, hash: str, file_name: str) -> None:
        """Download file from IPFS

        :param hash: IPFS hash of the directory with the logs
        :param file_name: Name of the file to download
        """

        try:
            _logger.debug(f"Downloading file {file_name} from IPFS...")
            response = requests.get(f"https://ipfs.io/ipfs/{hash}/{file_name}")
            if response.status_code == 200:
                _logger.info("IPFS: Succesfully download logs from ipfs.")
                print("IPFS: Succesfully download logs from ipfs.")
                with open(f"{self.temp_dir}/{file_name}", "wb") as f:
                    decrypted_content = decrypt_message(response.text, self.sender_public_key, ADMIN_SEED)
                    f.write(decrypted_content)
            elif response.status_code == 404:
                pass
            else:
                _logger.warning(f"Couldn't download logs from ipfs with response: {response}")
                print(f"Couldn't download logs from ipfs with response: {response}")

        except Exception as e:
            _logger.warning(f"Couldn't download logs {file_name} from ipfs: {e}")
            print(f"Couldn't download logs {file_name} from ipfs: {e}")

    def _download_logs(self, hash: str) -> None:
        """Download all the files from IPFS.

        :param hash: IPFS hash of the directory with the logs
        """

        for log in logs_name:
            self._download_file(hash, log)

        with open(f"{self.temp_dir}/issue_description.json") as f:
            metadata = json.load(f)
            pictures_count = metadata["pictures_count"]
            print(f"Pictures count: {pictures_count}")
            if int(pictures_count) > 0:
                for i in range(1, pictures_count + 1):
                    self._download_file(hash, f"picture{i}")

    def parse_logs(self, hash) -> tuple:
        """Parse description file."""
        self._download_logs(hash)
        _logger.info("Parsing logs...")
        print("Parsing logs...")
        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            email = issue["e-mail"]
            phone = issue["phone_number"]
            description = issue["description"]
        return email, phone, description

    def clean_temp_dir(self) -> None:
        """Remove the temporary directory and its content"""
        shutil.rmtree(self.temp_dir)
