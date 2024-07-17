import tempfile
import json
from dotenv import load_dotenv
import requests
import shutil
import os
from tenacity import *
from helpers.logger import Logger
from utils.decryption import decrypt_message
from rrs_operator.utils.reports import ReportsFabric

load_dotenv()

logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]

ADMIN_SEED = os.getenv("ADMIN_SEED")


class IPFSHelpder:
    def __init__(self, sender_public_key: str) -> None:
        self._logger = Logger("ipfs")
        self.sender_public_key = sender_public_key
        self.temp_dir = tempfile.mkdtemp()

    @retry(wait=wait_fixed(5))
    def _download_file(self, hash: str, file_name: str) -> None:
        """Download file from IPFS

        :param hash: IPFS hash of the directory with the logs
        :param file_name: Name of the file to download
        """

        try:
            self._logger.debug(f"Downloading file {file_name} from IPFS...")
            response = requests.get(f"https://gateway.pinata.cloud/ipfs/{hash}/{file_name}")
            if response.status_code == 200:
                self._logger.info("IPFS: Succesfully download logs from ipfs.")
                with open(f"{self.temp_dir}/{file_name}", "w") as f:
                    decrypted_content = decrypt_message(response.text, self.sender_public_key, self._logger)
                    f.write(decrypted_content)
            elif response.status_code == 404:
                pass
            else:
                self._logger.error(f"Couldn't download logs from ipfs with response: {response}")
                raise Exception("Couldn't download logs from ipfs")

        except Exception as e:
            self._logger.error(f"Couldn't download logs {file_name} from ipfs: {e}")
            raise (e)

    def _download_logs(self, hash: str) -> None:
        """Download all the files from IPFS.

        :param hash: IPFS hash of the directory with the logs
        """

        for log in logs_name:
            self._download_file(hash, log)

        with open(f"{self.temp_dir}/issue_description.json") as f:
            metadata = json.load(f)
            pictures_count = metadata["pictures_count"]
            if int(pictures_count) > 0:
                for i in range(1, pictures_count + 1):
                    self._download_file(hash, f"picture{i}")

    def parse_logs(self, hash) -> tuple:
        """Parse description file."""
        self._download_logs(hash)
        self._logger.info(f"IPFS:  Parsing logs... Hash: {hash}")

        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            if isinstance(issue["description"], dict):
                description_type = issue["description"]["type"]
                unparsed_description = issue["description"]["description"]
            else:
                description_type = "errors"
                unparsed_description = issue["description"]
            report = ReportsFabric.get_report(description_type)
            description = report.get_descriptions(unparsed_description)
            priority = report.get_priority()
        return description, priority

    def clean_temp_dir(self) -> None:
        """Remove the temporary directory and its content"""
        shutil.rmtree(self.temp_dir)
