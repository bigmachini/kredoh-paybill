from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Transaction:
    transaction_type: str
    transaction_id: str
    transaction_time: str
    transaction_amount: int
    business_short_code: str
    bill_reference_number: str
    invoice_number: str
    org_account_balance: float
    third_party_transaction_id: str
    msisdn: str
    first_name: str
    middle_name: str
    last_name: str


class C2BRequest(BaseModel):
    TransactionType: str
    TransID: str
    TransTime: str
    TransAmount: str
    BusinessShortCode: str
    BillRefNumber: str
    InvoiceNumber: str
    OrgAccountBalance: str
    ThirdPartyTransID: str
    MSISDN: str
    FirstName: str
    MiddleName: str
    LastName: str
