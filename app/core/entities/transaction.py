from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_type: str
    transaction_id: str
    transaction_time: str
    transaction_amount: str
    business_short_code: str
    bill_reference_number: str
    invoice_number: str
    org_account_balance: str
    third_party_transaction_id: str
    msisdn: str
    first_name: str
    middle_name: str
    last_name: str
