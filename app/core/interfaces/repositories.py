from abc import ABC, abstractmethod

from app.core.entities.transaction import Transaction


class IRepository(ABC):
    @abstractmethod
    def save_record(self, data: dict, table_name: str) -> None:
        pass
