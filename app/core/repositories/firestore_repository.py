from typing import Tuple, Any

from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

from app import _logger
from app.core.interfaces.repositories import IRepository


class FirestoreRepository(IRepository):

    def __init__(self):
        self.db = firestore.Client()

    def save_record(self, data: dict, table_name: str, _id: [str, int] = None) -> Tuple[Any, Any]:
        # create a new document in the table_name
        if _id is None:
            return self.db.collection(table_name).add(data)
        else:
            return self.db.collection(table_name).add(data, document_id=_id)

    def get_record(self, column: str, value: Any, table_name: str) -> Any:
        # Get a document from Firestore based on column name, value, and table name
        query = self.db.collection(table_name).where(filter=FieldFilter(column, "==", value))
        documents = query.get()

        for document in documents:
            return document.to_dict()

        return None

    def update_record(self, _id: [str, int], column: str, value: Any, table: str) -> None:
        # Create a reference to the Firestore document
        document_ref = self.db.collection(table).document(_id)

        # Update the document with the new value
        document_ref.set({column: value}, merge=True)
        _logger.log_text(f"Firestore table '{table}' with ID '{_id}' updated successfully.")
