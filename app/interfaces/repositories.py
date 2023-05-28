from abc import ABC, abstractmethod

from app.core.entities.transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> None:
        pass
