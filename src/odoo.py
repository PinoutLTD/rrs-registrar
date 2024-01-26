from .odoo_internal import OdooHelper
from tenacity import *
import typing as tp


class OdooProxy:
    """Proxy to work with Odoo. Uses OdooHelper class and exapnds it with retrying decorators."""

    def __init__(self) -> None:
        self.odoo_helper = OdooHelper()

    @retry(wait=wait_fixed(5))
    def create_rrs_user(self, email: str, owner_address: str, controller_address: str) -> int:
        """Creats user until it will be created.
        :param email: Customer's email address
        :param owner_address: Customer's address in Robonomics parachain
        :param controller_address: Controller's address in Robonomics parachain

        :return: User id
        """
        self.odoo_helper._logger.debug("Creating rrs user...")
        user_id = self.odoo_helper.create_rrs_user(email, owner_address, controller_address)
        if not user_id:
            raise Exception("Failed to create rrs user")
        self.odoo_helper._logger.debug(f"Rrs user created. User id: {user_id}")
        return user_id

    @retry(wait=wait_fixed(5))
    def create_invoice(self, address: str, email: str) -> int:
        """Creats invoice until it will be created.
        :param address: Owner's address in Robonomics parachain for the reference
        """
        self.odoo_helper._logger.debug("Creating invoice...")
        customer_id = self._create_customer(email, address)
        invoice_id = int(self.odoo_helper.create_invoice(address, customer_id))
        if not invoice_id:
            raise Exception("Failed to create invoice")
        self.odoo_helper._logger.debug(f"Invoice created.")
        try:
            is_posted = self.odoo_helper.post_invoice(invoice_id)
            self.odoo_helper._logger.debug(f"Invoice posted: {is_posted}")
        except Exception as e:
            self.odoo_helper._logger.error(f"Couldn't post invoics: {e}")
        return invoice_id

    @retry(wait=wait_fixed(5))
    def _create_customer(self, email: str, address: str) -> int:
        """Creats customer until it will be created.
        :param email: Customer's email address
        :param address: Customer's address in Robonomics parachain for the reference

        :return: Customer id
        """
        self.odoo_helper._logger.debug("Creating customer...")
        customer_id = self.odoo_helper.create_customer(email, address)
        if not customer_id:
            raise Exception("Failed to create customer")
        self.odoo_helper._logger.debug(f"Customer created.")
        return int(customer_id)

    @retry(wait=wait_fixed(5))
    def update_rrs_user_with_pinata_creds(self, user_id: int, pinata_key: str, pinata_api_secret: str) -> None:
        """Update the customer profile with pinata credentials in RRS module.
        :param customer_id: Customer id
        :param pinata_key: Pinata API key
        :param pinata_api_secret: Pinata API secret key
        :return: bool        rrs_user_id = self.check_if_rrs_user_exists(controller_address)
        """
        self.odoo_helper._logger.debug("Updating customer with pinata creds...")
        is_updated = self.odoo_helper.update_rrs_user_with_pinata_creds(user_id, pinata_key, pinata_api_secret)
        if not is_updated:
            raise Exception("Failed to update the user")
        self.odoo_helper._logger.debug(f"User updated with pinata creds.")

    @retry(wait=wait_fixed(5))
    def update_rrs_user_with_subscription_status(self, user_id: int) -> None:
        """Update the customer profile with subscription status: true after the subscription was bought.
        :param customer_id: User id
        :return: bool
        """
        self.odoo_helper._logger.debug("Updating customer with subscription status...")
        is_updated = self.odoo_helper.update_rrs_user_with_subscription_status(user_id)
        if not is_updated:
            raise Exception("Failed to update the user")
        self.odoo_helper._logger.debug(f"User updated with subscription status.")

    @retry(wait=wait_fixed(5))
    def revoke_pinata_creds_from_rss_user(self, user_id: int) -> None:
        """Update the customer profile with subscription status: true after the subscription was bought.
        :param customer_id: User id
        :return: bool
        """
        self.odoo_helper._logger.debug("Revoking pinata key from customer profile...")
        is_updated = self.odoo_helper.revoke_pinata_creds_from_rss_user(user_id)
        if not is_updated:
            raise Exception("Failed to update the user")
        self.odoo_helper._logger.debug(f"Keys revoked.")

    @retry(wait=wait_fixed(5))
    def retrieve_pinata_creds(self, controller_address: str, rrs_user_id: int) -> tuple:
        """Retrieve pinata creds.
        :param controller_address: Controller's address in Robonomics parachain

        :return: The Pinata creds or None.
        """
        self.odoo_helper._logger.debug("Retrieving pinata creds from rrs user...")
        pinata_key, pinata_secret = self.odoo_helper.retrieve_pinata_creds(controller_address, rrs_user_id)
        if pinata_key is not None:
            return pinata_key, pinata_secret

    @retry(wait=wait_fixed(5))
    def check_if_rrs_user_exists(self, controller_address: str) -> tp.Union[int, bool]:
        """Looking for a rrs user id by the controller address.
        :param controller_address: Controller's address in Robonomics parachain.

        :return: The user id or false.
        """
        id = self.odoo_helper.check_if_rrs_user_exists(controller_address)
        return id

    @retry(wait=wait_fixed(5))
    def check_if_invoice_posted(self, owner_address: str) -> tp.Optional[int]:
        """Checks if invoice  for this account is posted.
        :param owner_address: Owner's address in Robonomics parachain for the reference

        :return: Invoice id
        """
        self.odoo_helper._logger.debug("Checking if invoice is posted...")
        id = self.odoo_helper.check_if_invoice_posted(owner_address)
        if id:
            return True
        return False
