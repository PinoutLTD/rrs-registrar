import re


def format_hash(hash) -> str:
    match = re.search(r'Qm\w+', hash)
    if match: 
        return match.group()