import re

def extract_hash(description: str) -> str:
    """Parses the description string from Odoo tickets to extract IPFS hash.
    
    :param description: Description from the ticket.

    :return: The hash.
    """
    pattern = r'Hash: (\S+)'
    match = re.search(pattern, description)
    if match:
        hash = match.group(1)
        return hash