from app.constants import C2B_PAYBILL
from app.core.entities.transaction import Transaction
from app.core.interfaces.services import ITransactionService
from app.core.repositories.firestore_repository import FirestoreRepository


class TransactionService(ITransactionService):
    def __init__(self, firestore_repository: FirestoreRepository):
        self.db = firestore_repository

    def process_transaction(self, transaction_data: dict) -> None:
        # Map the transaction data from the JSON payload to the Transaction entity
        transaction = Transaction(
            transaction_id=transaction_data.get("TransID"),
            transaction_time=transaction_data.get("TransTime"),
            transaction_amount=transaction_data.get("TransAmount"),
            business_short_code=transaction_data.get("BusinessShortCode"),
            bill_reference_number=transaction_data.get("BillRefNumber").replace(' ', ''),
            third_party_transaction_id=transaction_data.get("ThirdPartyTransID"),
            first_name=transaction_data.get("FirstName"),
        )

        # Save the transaction data
        self.db.save_record(transaction.__dict__, C2B_PAYBILL, transaction.transaction_id)
