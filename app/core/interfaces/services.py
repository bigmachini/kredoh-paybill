from abc import ABC, abstractmethod

from app.core.entities.transaction import Transaction


class ITransactionService(ABC):
    @abstractmethod
    def process_transaction(self, transaction_data: dict) -> None:
        pass
