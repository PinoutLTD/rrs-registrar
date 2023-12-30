import robonomicsinterface as ri
import os
from dotenv import load_dotenv
from substrateinterface import KeypairType

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")
WSS_ENDPOINT = os.getenv("WSS_ENDPOINT")


def transfer_xrt_2buy_subscription(owner_address: str) -> str:
    """Sends XRT tokens to the owner address to buy a subscription.

    :param owner_address: Address of the subscription's owner.
    :return: Hash of the transfer transaction.
    """
    account = ri.Account(remote_ws=WSS_ENDPOINT, seed=ADMIN_SEED, crypto_type=KeypairType.ED25519)
    subscription_price = 10**9 + 3
    ri_common_functions = ri.CommonFunctions(account=account)
    return ri_common_functions.transfer_tokens(target_address=owner_address, tokens=subscription_price)
