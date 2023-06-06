from typing import Any, Tuple

from app.core.entities.kyanda import KyandaIPNRequest, KyandaIPN
from app.core.repositories.firestore_repository import FirestoreRepository


class KyandaService:
    def __init__(self, firestore_repository: FirestoreRepository):
        self.db = firestore_repository

    def process_ipn(self, payload: KyandaIPNRequest) -> Tuple[Any, Any]:
        ipn = KyandaIPN(
            destination=payload.destination,
            merchant_id=payload.MerchantID,
            details=payload.details,
            request_meta_data=payload.requestMetadata,
            status=payload.status,
            status_code=payload.status_code,
            message=payload.message,
            transaction_date=payload.transactionDate,
            transaction_ref=payload.transactionRef,
            amount=payload.amount
        )

        if ipn.status.upper() == "SUCCESS" or ipn.status_code == "0000":
            table_name = "kyanda-ipn"
        else:
            table_name = "kyanda-ipn-failed"

        with self.db.save_record(ipn.__dict__, table_name, ipn.transaction_ref):
            return None  # Return None or any other desired value as per your use case
