from rrs_operator.src.robonomics import RobonomicsHelper
from rrs_operator.src.odoo import Odoo
from rrs_operator.src.ipfs import IPFSHelpder

class Operator:
    def __init__(self) -> None:
        self.odoo = Odoo()
        self.robonomics = RobonomicsHelper(self.odoo)
        self.robonomics.subscribe()
    
    def get_robonomics_add_user_callback(self) -> None:
        return self.robonomics.add_user_callback

    def get_unpin_logs_from_IPFS_callback(self):
        return IPFSHelpder.unpin_hash_from_IPFS