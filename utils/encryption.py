import json
import os
import typing as tp

from dotenv import load_dotenv
from robonomicsinterface import Account
from substrateinterface import Keypair, KeypairType

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")

def encrypt_for_users(data: str, users: tp.List[str], logger) -> str:
    """
    Encrypt data for random generated private key, then encrypt this key for user from the list

    :param data: Data to encrypt
    :param sender_kp: ED25519 account keypair that encrypts the data
    :param users: List of ss58 ED25519 addresses

    :return: JSON string consists of encrypted data and a key encrypted for all accounts in the subscription
    """
    try:
        account = Account(ADMIN_SEED, crypto_type=KeypairType.ED25519)
        admin_keypair = account.keypair
        random_seed = Keypair.generate_mnemonic()
        random_acc = Account(random_seed, crypto_type=KeypairType.ED25519)
        encrypted_data = _encrypt_message(
            str(data), admin_keypair, random_acc.keypair.public_key
        )
        encrypted_keys = {}
        for user in users:
            try:
                receiver_kp = Keypair(
                    ss58_address=user, crypto_type=KeypairType.ED25519
                )
                encrypted_key = _encrypt_message(
                    random_seed, admin_keypair, receiver_kp.public_key
                )
                encrypted_keys[user] = encrypted_key
            except Exception as e:
                logger.error(
                    f"Faild to encrypt key for: {user} with error: {e}. Check your RWS users, you may have SR25519 address in users."
                )
        encrypted_keys["data"] = encrypted_data
        data_final = json.dumps(encrypted_keys)
        return data_final
    except Exception as e:
        logger.error(f"Exception in encrypt for users: {e}")

def _encrypt_message(
    message: tp.Union[bytes, str], admin_keypair: Keypair, recipient_public_key: bytes
) -> str:
    """Encrypt message with sender private key and recipient public key

    :param message: Message to encrypt
    :param admin_keypair: Admin account Keypair
    :param recipient_public_key: Recipient public key

    :return: encrypted message
    """

    encrypted = admin_keypair.encrypt_message(message, recipient_public_key)
    return f"0x{encrypted.hex()}"