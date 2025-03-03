import json
import os
import typing as tp

from dotenv import load_dotenv
from robonomicsinterface import Account
from substrateinterface import Keypair, KeypairType

load_dotenv()
ADMIN_SEED = os.getenv("ADMIN_SEED")

def encrypt_message(
    message: tp.Union[bytes, str],
    address: str,
    logger
) -> str:
    """Encrypt message with sender private key and recipient public key

    :param message: Message to encrypt
    :param sender_keypair: Sender account Keypair
    :param recipient_public_key: Recipient public key

    :return: encrypted message
    """
    account = Account(ADMIN_SEED, crypto_type=KeypairType.ED25519)
    sender_keypair = account.keypair
    recipient_kp = Keypair(ss58_address=address)
    encrypted = sender_keypair.encrypt_message(message, recipient_kp.public_key)
    return f"0x{encrypted.hex()}"