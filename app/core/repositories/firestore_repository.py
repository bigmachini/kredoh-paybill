import os
from google.cloud import firestore

from app.core.entities.transaction import Transaction
from app.interfaces.repositories import TransactionRepository


class FirestoreRepository(TransactionRepository):
    def __init__(self):
        self.db = firestore.Client.from_service_account_json(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )

    def save_transaction(self, transaction: Transaction) -> None:
        # Convert the Transaction entity to a dictionary
        transaction_data = transaction.__dict__

        # Remove the 'transaction_id' field as Firestore will generate its own ID
        transaction_data.pop("transaction_id")

        # Create a new document in the 'transactions' collection
        self.db.collection("transactions").add(transaction_data)
