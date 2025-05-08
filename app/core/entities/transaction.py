from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


@dataclass
class Transaction:
    transaction_id: str
    transaction_time: str
    transaction_amount: float
    business_short_code: str
    bill_reference_number: str
    third_party_transaction_id: str
    first_name: str


class C2BRequest(BaseModel):
    TransID: str
    TransTime: Optional[str] = None
    TransAmount: Optional[str] = None
    BusinessShortCode: Optional[str] = None
    BillRefNumber: Optional[str] = None
    ThirdPartyTransID: Optional[str] = None
    FirstName: Optional[str] = None
