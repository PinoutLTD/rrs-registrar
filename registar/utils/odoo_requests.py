
def save_cid_and_orderid(odoo, cid: str, order_id: str, email: str):
    return odoo.save_cid_and_orderid(cid, order_id, email)

def save_orderid(odoo, cid: str, order_id):
    return odoo.save_orderid(cid, order_id)

def update_last_paid(odoo, order_id: str):
    return odoo.update_last_paid(order_id)

def set_status_not_paid(odoo, order_id: str):
    return odoo.set_status_not_paid(order_id)