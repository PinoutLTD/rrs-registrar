import robonomicsinterface as ri
import os
from dotenv import load_dotenv
from substrateinterface import KeypairType

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")
WSS_ENDPOINT = os.getenv("WSS_ENDPOINT")
ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")

def add_device_to_subscription(address: str) -> bool:
    """ Checks whether the address has an active subscription or not.
    :param owner_address: Address of the subscription's owner.

    :return True if subscription is active, False otherwise
    """
    account = ri.Account(remote_ws=WSS_ENDPOINT, seed=ADMIN_SEED, crypto_type=KeypairType.ED25519)
    rws = ri.RWS(account)
    devices = rws.get_devices(ADMIN_ADDRESS)
    print(f"Devices before update: {devices}")
    devices.append(address)
    print(f"Devices after update: {devices}")

    return rws.set_devices(devices)

