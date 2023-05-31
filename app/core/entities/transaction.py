from dataclasses import dataclass

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
    TransTime: str
    TransAmount: str
    BusinessShortCode: str
    BillRefNumber: str
    ThirdPartyTransID: str
    FirstName: str
