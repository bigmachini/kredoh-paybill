from app.constants import C2B_PAYBILL, REVERSAL_CALLBACK
from app.core.entities.safaricom import ReversalCallback, ReversalCallbackRequest
from app.core.entities.transaction import Transaction
from app.core.interfaces.services import ISafaricomService
from app.core.repositories.firestore_repository import FirestoreRepository


class SafaricomService(ISafaricomService):

    def __init__(self, firestore_repository: FirestoreRepository):
        self.db = firestore_repository

    def process_c2b(self, transaction_data: dict) -> None:
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

    def process_reversal_callback(self, body: ReversalCallbackRequest) -> None:
        # Map the transaction data from the JSON payload to the Transaction entity
        callback = ReversalCallback(
            transaction_id=body.TransactionID,
            result_code=body.ResultCode,
            conversation_id=body.ConversationID,
            originator_conversation_id=body.OriginatorConversationID,
            result_desc=body.ResultDesc,
            result_type=body.ResultType,
        )

        # Save the transaction data
        self.db.save_record(callback.__dict__, REVERSAL_CALLBACK, callback.transaction_id)
