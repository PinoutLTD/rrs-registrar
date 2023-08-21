import tempfile
import json
import requests
import logging
import os

logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]
# logger = logging.getLogger("__ipfs__")
# logger.setLevel("DEBUG")


class IPFSHelpder:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel("DEBUG")
        print(self.logger)

    def _download_logs_dir(self, hash: str) -> str:
        self.temp_dir = tempfile.mkdtemp()
        self.logger.info(f"Temp dir: {self.temp_dir}")
        
        for log in logs_name:
            try:
                self.logger.debug(f"Downloading file {log} from IPFS...")
                response = requests.get(f"https://ipfs.io/ipfs/{hash}/{log}")
                if response.status_code == 200:
                    self.logger.info("IPFS: Succesfully download logs from ipfs.")
                    with open(f"{self.temp_dir}/{log}", "w") as f:
                        f.write(str(response.content))
                        print(response.content)
                elif response.status_code == 404:
                    pass
                else:
                    self.logger.warning(f"Couldn't download logs from ipfs with response: {response}")

            except Exception as e:
                self.logger.warning(f"Couldn't download logs {log} from ipfs: {e}")

    def parse_logs(self, hash) -> tuple:
        self._download_logs_dir(hash)
        self.logger.info("Parsing logs...")
        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            email = issue["e-mail"]
            phone = issue["phone_number"]
            description = issue["description"]
        return email, phone, description

    def clean_temp_dir(self) -> None:
        self.temp_dir.cleanup()
