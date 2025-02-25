import typing as tp
from helpers.logger import Logger

class TicketManager:
    def __init__(self, odoo) -> None:
        self.odoo = odoo
        self._logger = Logger("ticket-manager")
    
    def process_ticket(self, descriptions_list, priority, source: str, email: str, sender_address: str, logs_hashes):
        ticket_ids = []
        paid_service = self.odoo.is_paid(sender_address)
        for description in descriptions_list:
            ticket_id = self._find_existing_ticket(description, email, source)
            if ticket_id:
                self._update_existing_ticket(ticket_id, description)
            else:
                ticket_id = self.odoo.create_ticket(email, sender_address, description, priority, source)
            ticket_ids.append(ticket_id)
            if logs_hashes:
                for hash in logs_hashes:
                    self.odoo.create_note_with_logs_hash(ticket_id, hash)
        return ticket_ids, paid_service

    def _find_existing_ticket(self, description: str, email: str, source: str) -> tp.Optional[int]:
        if (source == "devices") or (source == ""):
            ticket_id = self.odoo.find_ticket_with_description(description, email)
        else:
            ticket_id = self.odoo.find_ticket_with_source(source, email)
        return ticket_id
    
    def _update_existing_ticket(self, ticket_id: int, description: str):
        self.odoo.get_and_increase_problem_counter(ticket_id)
        self.odoo.set_last_occurred(ticket_id)
        current_description = self.odoo.get_description_from_ticket(ticket_id)
        if description in current_description:
            self._logger.debug(f"New descritpion is the same")
        else:
            self._logger.debug("New description is not the same. Adding to the ticket...")
            self.odoo.get_and_update_description(ticket_id, description)