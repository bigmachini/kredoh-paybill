from app.core.entities.transaction import Transaction
from app.core.interfaces.repositories import TransactionRepository
from app.core.services.safaricom_service import SafaricomService


class MockTransactionRepository(TransactionRepository):
    def save_transaction(self, transaction: Transaction) -> None:
        pass


def test_process_transaction():
    # Mock the repository
    mock_repository = MockTransactionRepository()

    # Create an instance of the service
    safaricom_service = SafaricomService(mock_repository)

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

    # Invoke the process_c2b method
    transaction_service.process_c2b(transaction_data)

    # Assert that the save_transaction method of the repository is called with the correct arguments
    mock_repository.save_transaction.assert_called_once()
