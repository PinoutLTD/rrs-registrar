import json
import os
import typing as tp

from dotenv import load_dotenv
from robonomicsinterface import Account
from substrateinterface import Keypair, KeypairType

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")

def decrypt_message(encrypted_message: str, sender_address: str, logger) -> str:
    recipient_acc = Account(ADMIN_SEED, crypto_type=KeypairType.ED25519)
    sender_kp = Keypair(ss58_address=sender_address)
    try:
        data_json = json.loads(encrypted_message)
    except:
        return _decrypt_message(encrypted_message, sender_kp.public_key, recipient_acc.keypair).decode("utf-8")
    try:
        if recipient_acc.get_address() in data_json:
            decrypted_seed = _decrypt_message(
                data_json[recipient_acc.get_address()],
                sender_kp.public_key,
                recipient_acc.keypair,
            ).decode("utf-8")
            decrypted_acc = Account(decrypted_seed, crypto_type=KeypairType.ED25519)
            decrypted_data = _decrypt_message(
                data_json["data"], sender_kp.public_key, decrypted_acc.keypair
            ).decode("utf-8")
            return decrypted_data
        else:
            logger.error(f"Error in decrypt for devices: account is not in devices")
    except Exception as e:
        logger.error(f"Exception in decrypt for devices: {e}")

def _decrypt_message(encrypted_message: str, sender_public_key: bytes, admin_keypair) -> str:
    """Decrypt message with recepient private key and sender puplic key
    :param encrypted_message: Message to decrypt
    :param sender_public_key: Sender public key

    :return: Decrypted message
    """
    if encrypted_message[:2] == "0x":
        encrypted_message = encrypted_message[2:]
    bytes_encrypted = bytes.fromhex(encrypted_message)

    return admin_keypair.decrypt_message(bytes_encrypted, sender_public_key)