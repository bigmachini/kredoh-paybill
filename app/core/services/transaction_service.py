from app.core.entities.transaction import Transaction
from app.interfaces.repositories import TransactionRepository
from app.interfaces.services import TransactionService


class TransactionServiceImpl(TransactionService):
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    def process_transaction(self, transaction_data: dict) -> None:
        # Map the transaction data from the JSON payload to the Transaction entity
        transaction = Transaction(
            transaction_type=transaction_data.get("TransactionType"),
            transaction_id=transaction_data.get("TransID"),
            transaction_time=transaction_data.get("TransTime"),
            transaction_amount=transaction_data.get("TransAmount"),
            business_short_code=transaction_data.get("BusinessShortCode"),
            bill_reference_number=transaction_data.get("BillRefNumber"),
            invoice_number=transaction_data.get("InvoiceNumber"),
            org_account_balance=transaction_data.get("OrgAccountBalance"),
            third_party_transaction_id=transaction_data.get("ThirdPartyTransID"),
            msisdn=transaction_data.get("MSISDN"),
            first_name=transaction_data.get("FirstName"),
            middle_name=transaction_data.get("MiddleName"),
            last_name=transaction_data.get("LastName"),
        )

        # Save the transaction data
        self.transaction_repository.save_transaction(transaction)
