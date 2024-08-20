import json
import os
import shutil
import tempfile

import ipfshttpclient2
import requests
from dotenv import load_dotenv
from tenacity import *

from helpers.logger import Logger
from rrs_operator.utils.reports import ReportsFabric
from utils.decryption import decrypt_message

load_dotenv()

logs_name = ["issue_description.json", "home-assistant.log", "trace.saved_traces"]

ADMIN_SEED = os.getenv("ADMIN_SEED")
IPFS_ENDPOINT = os.getenv("IPFS_ENDPOINT")


class IPFSHelpder:
    def __init__(self, sender_public_key: str) -> None:
        self._logger = Logger("ipfs")
        self.sender_public_key = sender_public_key
        self.temp_dir = tempfile.mkdtemp()
        self.logs_hashes = []

    def parse_logs(self, hash) -> tuple:
        """Parses description file."""
        self._download_logs_and_pin_to_IPFS(hash)
        self._logger.info(f"IPFS:  Parsing logs... Hash: {hash}")
        
        with open(f"{self.temp_dir}/issue_description.json") as f:
            issue = json.load(f)
            self._logger.debug(f"Description full: {issue['description']}, type {type(issue['description'])}")
            if isinstance(issue['description'], dict):
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

    @retry(wait=wait_fixed(5))
    def _download_file(self, hash: str, file_name: str) -> None:
        """Downloads file from IPFS

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

    def _download_logs_and_pin_to_IPFS(self, hash: str) -> None:
        """Downloads all the files from IPFS and adds decrypted
           content to IPFS.

        :param hash: IPFS hash of the directory with the logs
        """

        for log in logs_name:
            self._download_file(hash, log)
            self._pin_file_to_IPFS(log)

        with open(f"{self.temp_dir}/issue_description.json") as f:
            metadata = json.load(f)
            pictures_count = metadata["pictures_count"]
            if int(pictures_count) > 0:
                for i in range(1, pictures_count + 1):
                    self._download_file(hash, f"picture{i}")
    

    def _pin_file_to_IPFS(self, file_name: str) -> str:
        """Pin decrypted logs to IPFS local node. Saves the hash.

        :param file_name: Name of the log file.
        """

        self._logger.debug(f"Pinning {self.temp_dir}/{file_name} to the local node...")
        if file_name == "issue_description.json":
            return
        with ipfshttpclient2.connect(IPFS_ENDPOINT) as client:
            response = client.add(f"{self.temp_dir}/{file_name}")
            self._logger.debug(f"Done pinning. Response is: {response}")
            self.logs_hashes.append(response["Hash"])

