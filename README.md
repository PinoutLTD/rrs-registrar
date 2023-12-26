## Robonomics Report Service

The service facilitates registration through Libp2p messages via a WebSocket connection. It leverages the [proxy](https://github.com/PinoutLTD/libp2p-ws-proxy) to retrieve Libp2p messages. Upon receiving the registration messages, a new user is created in the [Odoo Robonomics Report Service addon](https://github.com/PinoutLTD/rrs-odoo-addon) using the Odoo API. Subsequently, a Pinata API key is generated, and XRT tokens are dispatched to the customer's address for subscription purchase. This service runs a Flask app on the 5000 port so it should be available. 

---

Requirements:

1. python3.10
2. Odoo with the [Robonomics Report Service](https://github.com/PinoutLTD/rrs-odoo-addon) module installed.
3. Robonomics account ED25519 type with XRT on it.
4. Pinata API keys with admin permissions.
5. [Libp2p-ws proxy](https://github.com/PinoutLTD/libp2p-ws-proxy) installed.

---

Installation:

```
git clone https://github.com/PinoutLTD/rrs-registrar.git
pip3 -r requirements.txt
cp template.env .env
```
Set the configuration file by specifying Odoo, Robonomics and Pinata credentials.

Launch:
```
python3 main.py
```