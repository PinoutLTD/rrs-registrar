import requests
import json
import typing as tp


def generate_pinata_keys(api_key: str, api_secret_key: str, key_name: str) -> tp.Dict[str, str]:
    url = "https://api.pinata.cloud/users/generateApiKey"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret_key,
    }
    headers["Content-Type"] = "application/json"
    body = {
        "permissions": {"endpoints": {"pinning": {"pinFileToIPFS": True, "unpin": True}}},
        "keyName": key_name
    }

    response = requests.post(url, json=body, headers=headers)
    return json.loads(response.text)
