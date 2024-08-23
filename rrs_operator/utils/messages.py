import json


def message_for_subscribing() -> str:
    msg = {"protocols_to_listen": ["/report"]}
    return json.dumps(msg)
