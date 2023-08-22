import tempfile
import json
import requests
from utils.logger import logger

_logger = logger("ipfs")
logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]


class IPFSHelpder:

    def _download_logs_dir(self, hash: str) -> str:
        self.temp_dir = tempfile.mkdtemp()
        _logger.info(f"Temp dir: {self.temp_dir}")
        print(f"Temp dir: {self.temp_dir}")

        for log in logs_name:
            try:
                _logger.debug(f"Downloading file {log} from IPFS...")
                response = requests.get(f"https://ipfs.io/ipfs/{hash}/{log}")
                if response.status_code == 200:
                    _logger.info("IPFS: Succesfully download logs from ipfs.")
                    with open(f"{self.temp_dir}/{log}", "wb") as f:
                        f.write(response.content)
                elif response.status_code == 404:
                    pass
                else:
                    _logger.warning(f"Couldn't download logs from ipfs with response: {response}")

            except Exception as e:
                _logger.warning(f"Couldn't download logs {log} from ipfs: {e}")

    def parse_logs(self, hash) -> tuple:
        self._download_logs_dir(hash)
        _logger.info("Parsing logs...")
        print("Parsing logs...")
        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            email = issue["e-mail"]
            phone = issue["phone_number"]
            description = issue["description"]
        return email, phone, description

    def clean_temp_dir(self) -> None:
        self.temp_dir.cleanup()
