import json
import os

from utils.encryption import encrypt_for_users

ADMIN_SEED = os.getenv("ADMIN_SEED")

def message_with_pinata_creds(pinata_key: str, pinata_secret: str, sender_address: str, logger) -> str:
    pinata_key_encrypted = encrypt_for_users(pinata_key, [sender_address], logger)
    pinata_secret_encrypted = encrypt_for_users(pinata_secret, [sender_address], logger)
    msg = {
        "protocol": f"/pinataCreds/{sender_address}",
        "serverPeerId": "",
        "save_data": False,
        "data": {"data": {"public": pinata_key_encrypted, "private": pinata_secret_encrypted}},
    }
    return json.dumps(msg)

def message_for_subscribing() -> str:
    msg = {"protocols_to_listen": ["/initialization"]}
    return json.dumps(msg)
