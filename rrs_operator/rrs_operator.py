from rrs_operator.src.odoo import Odoo
from rrs_operator.src.robonomics import RobonomicsHelper
from rrs_operator.utils.ipfs_helper import IPFSHelper


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
        for hash in hashes:
            IPFSHelper.unpin_hash(hash)