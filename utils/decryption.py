from substrateinterface import Keypair, KeypairType
from robonomicsinterface import Account
import typing as tp
import json
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")


def decrypt_message(data: tp.Union[str, dict], sender_address: str, logger) -> str:
    """Decrypt message that was encrypted fo devices

    :param data: Ancrypted data
    :param sender_address: Sender address
    :param recipient_keypair: Recepient account keypair

    :return: Decrypted message
    """
    try:
        account = Account(ADMIN_SEED, crypto_type=KeypairType.ED25519)
        admin_keypair = account.keypair
        sender_public_key = Keypair(ss58_address=sender_address, crypto_type=KeypairType.ED25519).public_key
        logger.debug(f"Start decrypt for device {admin_keypair.ss58_address}")
        if isinstance(data, str):
            data_json = json.loads(data)
        else:
            data_json = data
        if admin_keypair.ss58_address in data_json:
            decrypted_seed = _decrypt_message(
                data_json[admin_keypair.ss58_address],
                sender_public_key,
                admin_keypair,
            ).decode("utf-8")
            decrypted_acc = Account(decrypted_seed, crypto_type=KeypairType.ED25519)
            decrypted_data = _decrypt_message(data_json["data"], sender_public_key, decrypted_acc.keypair).decode(
                "utf-8"
            )
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