import os
import json
from .decrypt_encrypt_msg import encrypt_message

ADMIN_SEED = os.getenv("ADMIN_SEED")

def message_with_pinata_creds(pinata_key: str, pinata_secret: str, controller_address: str) -> str:
    pinata_key_encrypted = encrypt_message(pinata_key, ADMIN_SEED, controller_address)
    pinata_secret_encrypted = encrypt_message(pinata_secret, ADMIN_SEED, controller_address)
    msg = {
        "protocol": f"/pinataCreds/{controller_address}",
        "serverPeerId": "",
        "data": {"public": pinata_key_encrypted, "private": pinata_secret_encrypted},
    }
    return json.dumps(msg)
