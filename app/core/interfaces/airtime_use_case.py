# app/core/use_cases/airtime_use_case.py
from abc import ABC, abstractmethod
from app.core.entities.airtime import Airtime



class IAirtimeUseCase(ABC):
    @abstractmethod
    def buy_airtime(self, airtime: Airtime) -> dict:
        pass
