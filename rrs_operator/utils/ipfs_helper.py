import os

import ipfshttpclient2
from dotenv import load_dotenv
from termcolor import colored

from helpers.logger import Logger
from rrs_operator.utils.files_helper import FilesHelper

load_dotenv()
IPFS_ENDPOINT = os.getenv("IPFS_ENDPOINT")

class IPFSHelper:
    def __init__(self) -> None:
        self._logger = Logger("ipfs")
        self.logs_hashes = []
    
    def pin_file(self, path_to_file: str) -> None:
        with ipfshttpclient2.connect(IPFS_ENDPOINT) as client:
            response = client.add(path_to_file)
            self._logger.debug(f"Done pinning. Response is: {response}")
            self.logs_hashes.append(response["Hash"])
    
    @staticmethod
    def unpin_hash(hash: str) -> None:
        with ipfshttpclient2.connect(IPFS_ENDPOINT) as client:
            try:
                res = client.pin.rm(hash)
                print(f"Unpinned {res['Pins']}")
            except ipfshttpclient2.exceptions.ErrorResponse:
                print(f"Hash {hash} already unpinned.")
                pass

    @staticmethod
    def get_ipfs_file(hash: str) -> str:
        with ipfshttpclient2.connect(IPFS_ENDPOINT) as client:
            try:
                res = client.cat(hash)
                return res.decode('utf-8')
            except Exception as e:
                print(colored(f"Couldn't get hash {hash} from ipfs node: {e}", 'red'))
    



    


