from robonomicsinterface import Account
from substrateinterface import KeypairType, Keypair


def decrypt_message(encrypted_text: str, sender_address: str, admin_seed: str) -> bytes:
    """Decrypting data using admin private key and sender public key.

    :param encrypted_text: Encypted text from the file
    :param sender_address: Sender's address

    :return: Decrypted text
    """
    admin_keypair = Account(admin_seed, crypto_type=KeypairType.ED25519)
    sender_kp = Keypair(ss58_address=sender_address, crypto_type=KeypairType.ED25519)
    if encrypted_text[:2] == "0x":
        encrypted_text = encrypted_text[2:]
    bytes_encrypted = bytes.fromhex(encrypted_text)
    return admin_keypair.keypair.decrypt_message(bytes_encrypted, sender_kp.public_key)
