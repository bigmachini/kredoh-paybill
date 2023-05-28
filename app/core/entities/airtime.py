from dataclasses import dataclass
from typing import Optional


@dataclass
class Airtime:
    amount: int
    phone_number: str
    other_phone_number: str
    mpesa_code: str
    firebase_token: Optional[str] = None
    is_pin_less: Optional[bool] = False
    vendor: str = "kyanda"
