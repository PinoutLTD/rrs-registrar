import os
import typing as tp
import xmlrpc.client

from dotenv import load_dotenv

from helpers.logger import Logger

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")


class OdooHelper:
    def __init__(self, name_of_the_user: str) -> None:
        self._logger = Logger(f"odoo-helper-{name_of_the_user}")
        self._connection, self._uid = self._connect_to_db()

    def _connect_to_db(self):
        """Connect to Odoo db

        :return: Proxy to the object endpoint to call methods of the odoo models.
        """
        try:
            common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(ODOO_URL), allow_none=1)
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if uid == 0:
                raise Exception("Credentials are wrong for remote system access")
            else:
                self._logger.debug("Connection Stablished Successfully")
                connection = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(ODOO_URL))
                return connection, uid
        except Exception as e:
            self._logger.error(f"Couldn't connect to the db: {e}")

    def create(self, model: str, data: dict) -> tp.Optional[int]:
        """Method to create a new record in any Odoo table
        :param model: Name of the model in Odoo
        :param data: Data to create record with

        :return: Id of the new record
        """
        try:
            record_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                model,
                "create",
                [data],
            )
            return record_id
        except Exception as e:
            self._logger.error(f"Couldn't create a new record in {model}: {e}")
            return None

    def update(self, model: str, record_id: int, data: dict) -> bool:
        """Method to update the exhisting record. with the new data
        :param model: Name of the model in Odoo
        :param record_id: Id of the record to be updated.
        :param data: Data to write

        :return: True if updated successfuly, False otherwise
        """
        return self._connection.execute_kw(
            ODOO_DB,
            self._uid,
            ODOO_PASSWORD,
            model,
            "write",
            [[record_id], data],
        )

    def search(self, model: str, search_domains: list = []) -> list:
        """Looking for a record in the model with the specified domain.
        :param model: Name of the model in Odoo
        :param search_domains: Optional: A list of tuples that define the search criteria.
        Retrievs all records of the model if is empty.

        :return: List of record ids. If there  are no records matching the domain, returns an empty list.
        """
        ids = self._connection.execute_kw(ODOO_DB, self._uid, ODOO_PASSWORD, model, "search", [search_domains])
        return ids

    def read(self, model: str, record_ids: list, fields: list = []) -> list:
        """Method to fetch details of the records corresponding to the ids.
        :param model: Name of the model in Odoo
        :param record_ids: Ids of the records to fetch details for
        :param fields: Optional: Read only the fields. If emtpy, returns all fields

        :return: List of the records
        """

        data = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                model,
                "read",
                record_ids,
                {"fields": fields},
            )
        return data

    def unlink(self, model: str, record_ids: list) -> bool:
        """Method to delete records from the database. 
        :param model: Name of the model in Odoo
        :param record_ids: Ids of the records to delete

        :return: True if the deletion is successful.
        """
        try: 
            result = self._connection.execute_kw(ODOO_DB, self._uid, ODOO_PASSWORD, model, "unlink", record_ids)
            return result
        except Exception as e:
            self._logger.error(f"Couldn't unlink records {record_ids} in model {model}")