from google.cloud import firestore, secretmanager
from google.cloud.firestore_v1 import FieldFilter

from app.constants import AIRTIME_RESPONSE_SUCCESS
from app.core.entities.kyanda import KyandaIPNRequest, KyandaIPN
from app.core.repositories.firestore_repository import FirestoreRepository
from app.utils import reverse_airtime


class KyandaService:
    def __init__(self, firestore_repository: FirestoreRepository):
        self.db = firestore_repository

    def process_ipn(self, payload: KyandaIPNRequest):
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

        if ipn.status == "Failed":
            query = self.db.get_record('kyanda_ref', ipn.transaction_ref, AIRTIME_RESPONSE_SUCCESS)
            reverse_airtime(query['airtime_request']['mpesa_code'], query['airtime_request']['amount_paid'])

        self.db.save_record(ipn.__dict__, table_name, ipn.transaction_ref)
