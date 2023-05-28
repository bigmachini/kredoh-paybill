from app.core.entities.transaction import Transaction
from app.interfaces.repositories import TransactionRepository


class TransactionRepositoryImpl(TransactionRepository):
    def save_transaction(self, transaction: Transaction) -> None:
        # Implement the logic to save the transaction data to the data source
        pass
