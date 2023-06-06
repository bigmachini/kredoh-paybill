from dataclasses import dataclass

from pydantic import BaseModel


class KyandaIPNRequest(BaseModel):
    category: str
    source: str
    destination: str
    direction: str
    MerchantID: str
    details: dict
    status: str
    status_code: str
    requestMetadata: dict
    message: str
    transactionDate: str
    transactionRef: str
    amount: float


@dataclass
class KyandaIPN:
    destination: str
    merchant_id: str
    details: dict
    request_meta_data: dict
    status: str
    status_code: str
    message: str
    transaction_date: str
    transaction_ref: str
    amount: float
