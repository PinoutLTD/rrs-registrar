from robonomicsinterface import Account
from substrateinterface import KeypairType, Keypair


def decrypt_message(encrypted_text: str, sender_address: str, admin_seed: str) -> bytes:
    """Decrypting data using admin private key and sender public key.

    :param encrypted_text: Encypted text from the file
    :param sender_address: Sender's address
    :param admin_seed: Admin's seed phrase

    :return: Decrypted text
    """
    admin_keypair = Account(admin_seed, crypto_type=KeypairType.ED25519)
    sender_kp = Keypair(ss58_address=sender_address, crypto_type=KeypairType.ED25519).public_key
    if encrypted_text[:2] == "0x":
        encrypted_text = encrypted_text[2:]
    bytes_encrypted = bytes.fromhex(encrypted_text)
    return admin_keypair.keypair.decrypt_message(bytes_encrypted, sender_kp)


def encrypt_message(text2decrypt: str, admin_seed: str, receiver_address: str) -> str:
    """Encrypting data using admin private key and the receiver public key.

    :param text2decrypt: Text to encrypt
    :param admin_seed: Admin's seed phrase
    :param receiver_address: Receiver's address

    :return: Encrypted text
    """
    admin_keypair = Account(admin_seed, crypto_type=KeypairType.ED25519).keypair
    receiver_kp = Keypair(ss58_address=receiver_address, crypto_type=KeypairType.ED25519).public_key
    encrypted = admin_keypair.encrypt_message(text2decrypt, receiver_kp)
    return f"0x{encrypted.hex()}"
