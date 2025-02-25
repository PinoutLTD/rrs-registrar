import json


def message_for_subscribing() -> str:
    msg = {"protocols_to_listen": ["/report"]}
    return json.dumps(msg)

def message_report_response(datalog: bool, ticket_ids: list, sender_address: str) -> str:
    msg = {
        "protocol": f"/report/{sender_address}",
        "serverPeerId": "",
        "save_data": False, 
        "data": {"datalog": datalog, "ticket_ids": ticket_ids, "address": sender_address}
    }
    return json.dumps(msg)