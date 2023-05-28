from app.core.entities.kyanda import KyandaIPN, KyandaIPNRequest
from app.core.repositories.firestore_repository import FirestoreRepository


class KyandaService:
    def __init__(self, firestore_repository: FirestoreRepository):
        self.db = firestore_repository

    category: str
    source: str
    destination: str
    MerchantID: int
    details: str
    status: str
    status_code: str
    message: str
    transactionDate: str
    transactionRef: str
    amount: str

    def process_ipn(self, payload: KyandaIPNRequest) -> None:
        # Map the transaction data from the JSON payload to the Transaction entity
        ipn = KyandaIPN(
            category=payload.category,
            source=payload.source,
            destination=payload.destination,
            merchant_id=payload.MerchantID,
            details=payload.details,
            status=payload.status,
            status_code=payload.status_code,
            message=payload.message,
            transaction_date=payload.transactionDate,
            transaction_ref=payload.transactionRef,
            amount=int(float(payload.amount))
        )

        if ipn.status.upper() == "SUCCESS" or ipn.status_code == "0000":
            table_name = "kyanda-ipn"
        else:
            table_name = "kyanda-ipn-failed"

        return self.db.save_record(ipn.__dict__, table_name, ipn.transaction_ref)
