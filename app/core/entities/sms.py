from dataclasses import dataclass


@dataclass
class SMS:
    phone_number: str
    message: str
