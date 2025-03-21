
def save_cid_and_orderid(odoo, cid: str, order_id: str, email: str):
    return odoo.save_cid_and_orderid(cid, order_id, email)

def save_orderid(odoo, cid: str, order_id):
    return odoo.save_orderid(cid, order_id)

def update_last_paid(odoo, order_id: str):
    return odoo.update_last_paid(order_id)

def _is_paid(odoo, order_id):
    id = odoo.find_user_by_orderid(order_id)
    return odoo.is_paid(id)

def setup_new_paid_customer(odoo, order_id: str, unpin_logs_from_IPFS_callback):
    is_paid = _is_paid(odoo, order_id)
    if not is_paid:
        id = odoo.find_user_by_orderid(order_id)
        email = odoo.find_email_from_user_id(id)
        tickets_ids = odoo.find_tickets_by_email(email)
        for ticket in tickets_ids:
            unpin_logs_from_IPFS_callback(ticket)
            odoo.delete_ticket(int(ticket))

def set_status_not_paid(odoo, order_id: str):
    return odoo.set_status_not_paid(order_id)
