from abc import ABC, abstractmethod


class ISafaricomService(ABC):
    @abstractmethod
    def process_c2b(self, transaction_data: dict) -> None:
        pass

    @abstractmethod
    def process_reversal_callback(self, body: dict) -> None:
        pass
