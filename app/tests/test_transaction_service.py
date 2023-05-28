from unittest.mock import MagicMock

from app.core.services.transaction_service import TransactionServiceImpl
from app.core.entities.transaction import Transaction
from app.interfaces.repositories import TransactionRepository


class MockTransactionRepository(TransactionRepository):
    def save_transaction(self, transaction: Transaction) -> None:
        pass


def test_process_transaction():
    # Mock the repository
    mock_repository = MockTransactionRepository()

    # Create an instance of the service
    transaction_service = TransactionServiceImpl(mock_repository)

    # Define the input transaction data
    transaction_data = {
        "TransactionType": "Pay Bill",
        "TransID": "RKTQDM7W6S",
        "TransTime": "20191122063845",
        "TransAmount": "10",
        "BusinessShortCode": "600638",
        "BillRefNumber": "invoice008",
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "hashed",
        "FirstName": "John",
        "MiddleName": "",
        "LastName": "Doe"
    }

    # Invoke the process_transaction method
    transaction_service.process_transaction(transaction_data)

    # Assert that the save_transaction method of the repository is called with the correct arguments
    mock_repository.save_transaction.assert_called_once()
