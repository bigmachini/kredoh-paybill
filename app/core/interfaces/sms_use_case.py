# app/core/use_cases/airtime_use_case.py
from abc import ABC, abstractmethod

from app.core.entities.airtime import Airtime


class ISMSUseCase(ABC):
    @abstractmethod
    def send_sms(self, airtime: Airtime) -> dict:
        pass
