from abc import ABC, abstractmethod
from typing import Any


class IRepository(ABC):
    @abstractmethod
    def save_record(self, data: dict, table_name: str) -> None:
        pass

    @abstractmethod
    def get_record(self, column: str, value: Any, table_name: str) -> None:
        pass

    @abstractmethod
    def update_record(self, _id: str, column: str, value: Any, table_name: str) -> None:
        pass