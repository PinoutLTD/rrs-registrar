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

    def _download_logs_dir(self, hash: str) -> None:
        """Download files from IPFS, decrypted them and save them to the temporary directory

        :param hash: IPFS hash of the directory with the logs
        """

        _logger.info(f"Temp dir: {self.temp_dir}")
        print(f"Temp dir: {self.temp_dir}")
        print(f"Thread in download logs: {threading.current_thread()}")

        for log in logs_name:
            try:
                _logger.debug(f"Downloading file {log} from IPFS...")
                response = requests.get(f"https://ipfs.io/ipfs/{hash}/{log}")
                if response.status_code == 200:
                    _logger.info("IPFS: Succesfully download logs from ipfs.")
                    print("IPFS: Succesfully download logs from ipfs.")
                    with open(f"{self.temp_dir}/{log}", "wb") as f:
                        decrypted_content = decrypt_message(response.text, self.sender_public_key, ADMIN_SEED)
                        f.write(decrypted_content)
                elif response.status_code == 404:
                    pass
                else:
                    _logger.warning(f"Couldn't download logs from ipfs with response: {response}")
                    print(f"Couldn't download logs from ipfs with response: {response}")

            except Exception as e:
                _logger.warning(f"Couldn't download logs {log} from ipfs: {e}")
                print(f"Couldn't download logs {log} from ipfs: {e}")

    def parse_logs(self, hash) -> tuple:
        """Parse description file."""
        self._download_logs_dir(hash)
        _logger.info("Parsing logs...")
        print("Parsing logs...")
        print(f"Thread in parsing: {threading.current_thread()}")
        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            email = issue["e-mail"]
            phone = issue["phone_number"]
            description = issue["description"]
        return email, phone, description

    def clean_temp_dir(self) -> None:
        shutil.rmtree(self.temp_dir)
