import os
import typing as tp

import requests
from dotenv import load_dotenv
from pinatapy import PinataPy

from helpers.logger import Logger

load_dotenv()
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

class PinataHelper:
    
    @staticmethod
    def download_file(hash: str, logger: Logger) -> str:
        response = requests.get(f"https://ipfs.io/ipfs/{hash}")
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            pass
        else:
            logger.error(f"Couldn't download file {hash} from Pinata with response: {response}")
            raise Exception("Couldn't download file from Pinata")

    @staticmethod
    def download_file_from_directory(hash: str, file_name: str, logger: Logger) -> str:
        response = requests.get(f"https://gateway.pinata.cloud/ipfs/{hash}/{file_name}")
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            pass
        else:
            logger.error(f"Couldn't download file {file_name} from directory {hash} from Pinata with response: {response}")
            raise Exception("Couldn't download logs from Pinata")


    @staticmethod
    def unpin_file(hash: str, logger: Logger = None) -> tp.Dict[str, str]:
        pinata = PinataPy(PINATA_API_KEY, PINATA_API_SECRET)
        response = pinata.remove_pin_from_ipfs(hash)
        if response.get("message") == "Removed":
            if logger:
                logger.debug(f"Hash {hash} unpinned from Pinata")
        else:
            if logger:
                logger.error(f"Couldn't unpin hash: {response}")
    
    @staticmethod
    def generate_pinata_keys(key_name: str) -> tp.Dict[str, str]:
        pinata = PinataPy(PINATA_API_KEY, PINATA_API_SECRET)
        response = pinata.generate_api_key(
            key_name=key_name,
            is_admin=False,
            options={"permissions": {"endpoints": {"pinning": {"pinFileToIPFS": True, "unpin": True}}}},
        )
        return response

