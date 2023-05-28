import os

from google.cloud import firestore

from app.core.interfaces.repositories import IRepository


class FirestoreRepository(IRepository):
    def __init__(self):
        self.db = firestore.Client.from_service_account_json(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )

    def save_record(self, data: dict, table_name: str, _id: [str, int] = None) -> None:
        # create a new document in the table_name
        try:
            if _id is None:
                self.db.collection(table_name).add(data)
            else:
                self.db.collection(table_name).add(data, document_id=_id)
        except Exception as e:
            raise e
