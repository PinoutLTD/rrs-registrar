import json
import os

from utils.encryption import encrypt_message

ADMIN_SEED = os.getenv("ADMIN_SEED")
ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")

def message_with_pinata_creds(pinata_key: str, pinata_secret: str, sender_address: str, logger, paid: bool) -> str:
    pinata_key_encrypted = encrypt_message(pinata_key, sender_address, logger)
    pinata_secret_encrypted = encrypt_message(pinata_secret, sender_address, logger)
    msg = {
        "protocol": f"/initialization/{sender_address}",
        "serverPeerId": "",
        "save_data": False,
        "data": {"data": {"public": pinata_key_encrypted, "private": pinata_secret_encrypted, "paid": paid}},
    }
    return json.dumps(msg)

def message_for_subscribing() -> str:
    msg = {"protocols_to_listen": ["/initialization"]}
    return json.dumps(msg)

def message_with_robonomics_address(sender_address: str) -> str:
    msg = {
        "protocol": f"/initialization/{sender_address}",
        "serverPeerId": "",
        "save_data": False,
        "data": {"data": {"integrator_address": ADMIN_ADDRESS}},
    }
    return json.dumps(msg)

