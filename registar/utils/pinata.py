import typing as tp
from pinatapy import PinataPy


def generate_pinata_keys(admin_api_key: str, admin_api_secret_key: str, key_name: str) -> tp.Dict[str, str]:
    pinata = PinataPy(admin_api_key, admin_api_secret_key)
    response = pinata.generate_api_key(
        key_name=key_name,
        is_admin=False,
        options={"permissions": {"endpoints": {"pinning": {"pinFileToIPFS": True, "unpin": True}}}},
    )
    return response


def revoke_pinata_key(admin_api_key: str, admin_api_secret_key: str, key_to_revoke: str) -> tp.Dict[str, str]:
    pinata = PinataPy(admin_api_key, admin_api_secret_key)
    response = pinata.revoke_api_key(api_key=key_to_revoke)
    return response

def unpin_hash_from_pinata(admin_api_key: str, admin_api_secret_key: str, hash: str) -> tp.Dict[str, str]:
    pinata = PinataPy(admin_api_key, admin_api_secret_key)
    response = pinata.remove_pin_from_ipfs(hash)
    return response
