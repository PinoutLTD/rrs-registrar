from rrs_operator.src.robonomics import RobonomicsHelper
from rrs_operator.src.odoo import Odoo
import ipfshttpclient2
import os
from dotenv import load_dotenv

IPFS_ENDPOINT = os.getenv("IPFS_ENDPOINT")

class Operator:
    def __init__(self) -> None:
        self.odoo = Odoo()
        self.robonomics = RobonomicsHelper(self.odoo)
        self.robonomics.subscribe()
    
    def get_robonomics_add_user_callback(self) -> None:
        return self.robonomics.add_user_callback

    def get_unpin_logs_from_IPFS_callback(self):
        return self._get_and_unpin_hashes_from_ipfs

    def _get_and_unpin_hashes_from_ipfs(self, ticket_id: int) -> None:
        hashes = self.odoo.get_hashes_from_ticket(ticket_id)
        client = ipfshttpclient2.connect(IPFS_ENDPOINT)
        for hash in hashes:
            print(f"Unpinning {hash} from the local node...")
            try:
                res = client.pin.rm(hash)
                print(f"Unpinned {res['Pins']}")
            except ipfshttpclient2.exceptions.ErrorResponse:
                print(f"Hash {hash} already unpinned.")
                pass
        client.close()