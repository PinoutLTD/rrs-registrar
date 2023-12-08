## Robonomics Report Service

The service facilitates registration through Libp2p messages via a WebSocket connection. It leverages the [proxy](https://github.com/tubleronchik/libp2p-ws-proxy) to retrieve Libp2p messages. Upon receiving the registration messages, a new user is created in the [Odoo Robonomics Report Service](https://github.com/tubleronchik/odoo-robonomics-report-service) using the Odoo API. Reports are subsequently obtained through Robonomics Launches and stored in the Odoo Helpdesk module.