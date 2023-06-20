from fastapi import APIRouter, HTTPException, status

from app.constants import ALLOWED_TELCOS, DUPLICATE_TRANSACTION_ERROR
from app.core.entities.airtime import Airtime
from app.core.entities.kyanda import KyandaIPNRequest
from app.core.entities.safaricom import Reversal
from app.core.entities.sms import SMS
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.kyanda_service import KyandaService
from app.core.services.transaction_service import TransactionService
from app.core.use_cases.bonga_sms_use_case import SMSUseCaseBonga
from app.core.use_cases.kyanda_airtime_use_case import AirtimeUseCaseKyanda
from app.utils import get_carrier_info

router = APIRouter()
transaction_service = TransactionService(FirestoreRepository())
airtime_services = {"kyanda": AirtimeUseCaseKyanda()}
sms_services = {"bonga": SMSUseCaseBonga()}
db = FirestoreRepository()
callback_services = {"kyanda": KyandaService(db)}


@router.post("/confirmation", status_code=status.HTTP_200_OK)
def create_transaction(transaction: C2BRequest):
    print("api::create_transaction::transaction", transaction)
    try:
        transaction_data = transaction.dict()
        print("api::create_transaction::transaction_data", transaction_data)
        transaction_service.process_transaction(transaction_data)
        return {"message": "Transaction created successfully"}
    except Exception as ex:
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])


@router.post("/buy_airtime", status_code=status.HTTP_200_OK)
def buy_airtime(airtime: Airtime):
    print("api::buy_airtime::airtime", airtime)

    try:
        airtime_services[airtime.vendor].buy_airtime(airtime)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))


@router.post("/validation", status_code=status.HTTP_200_OK)
def validation_api(transaction: C2BRequest):
    print("api::validation_api::transaction", transaction)

    carrier = get_carrier_info(transaction.BillRefNumber)
    print("carrier", carrier)
    if carrier and carrier[0] in ALLOWED_TELCOS and float(transaction.TransAmount) >= 10 and float(
            transaction.TransAmount) <= 5000:
        return {
            "ResultCode": "0",
            "ResultDesc": "Accepted",
        }
    else:
        return {
            "ResultCode": "C2B00011",
            "ResultDesc": "Rejected",
        }


@router.post("/callback/kyanda", status_code=status.HTTP_201_CREATED)
def callback_kyanda(kyanda_ipn: KyandaIPNRequest):
    print("api::callback_kyanda::kyanda_ipn", kyanda_ipn)

    try:
        callback_services["kyanda"].process_ipn(kyanda_ipn)
        return {"message": "Record saved successfully"}
    except Exception as ex:
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])


@router.post("/send_sms", status_code=status.HTTP_200_OK)
def send_sms(sms: SMS):
    print("api::send_sms::sms", sms)

    try:
        sms_services[sms.vendor].send_sms(sms)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))


@router.post("/reversal", status_code=status.HTTP_200_OK)
def reversal(body: Reversal):
    print("api::reversal::body", body)

    try:
        sms_services[sms.vendor].send_sms(sms)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))
