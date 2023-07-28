from fastapi import APIRouter, HTTPException, status

from app import _logger
from app.constants import ALLOWED_TELCOS, DUPLICATE_TRANSACTION_ERROR
from app.core.entities.airtime import Airtime
from app.core.entities.kyanda import KyandaIPNRequest
from app.core.entities.safaricom import Reversal, ReversalCallbackResult
from app.core.entities.sms import SMS
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.kyanda_service import KyandaService
from app.core.services.safaricom_service import SafaricomService
from app.core.use_cases.bonga_sms_use_case import SMSUseCaseBonga
from app.core.use_cases.kyanda_airtime_use_case import AirtimeUseCaseKyanda
from app.core.use_cases.safaricom_use_case import SafaricomUseCase
from app.utils import get_carrier_info, reverse_airtime

router = APIRouter()
safaricom_service = SafaricomService(FirestoreRepository())
airtime_services = {"kyanda": AirtimeUseCaseKyanda()}
sms_services = {"bonga": SMSUseCaseBonga()}
db = FirestoreRepository()
callback_services = {"kyanda": KyandaService(db)}


@router.post("/confirmation", status_code=status.HTTP_200_OK)
def create_transaction(transaction: C2BRequest):
    _logger.log_text(f"api::create_transaction::transaction {transaction.__dict__}")
    try:
        carrier = get_carrier_info(transaction.BillRefNumber)
        _logger.log_text(f"carrier {carrier}")
        if carrier and carrier[0] in ALLOWED_TELCOS and float(transaction.TransAmount) >= 10 and float(
                transaction.TransAmount) <= 5000:
            transaction_data = transaction.dict()
            _logger.log_text(f"api::create_transaction::transaction_data {transaction_data}")
            safaricom_service.process_c2b(transaction_data)
            return {"message": "Transaction created successfully"}
        else:
            reverse_airtime(transaction.TransID, int(float(transaction.TransAmount)))
    except Exception as ex:
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])


@router.post("/buy_airtime", status_code=status.HTTP_200_OK)
def buy_airtime(airtime: Airtime):
    _logger.log_text(f"api::buy_airtime::airtime {airtime.__dict__}")

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
    _logger.log_text(f"api::validation_api::transaction {transaction.__dict__}")

    carrier = get_carrier_info(transaction.BillRefNumber)
    _logger.log_text(f"carrier {carrier}")
    if carrier and carrier[0] in ALLOWED_TELCOS and float(transaction.TransAmount) >= 5 and float(
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
    _logger.log_text(f"api::callback_kyanda::kyanda_ipn {kyanda_ipn.__dict__}")

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
    _logger.log_text(f"api::send_sms::sms {sms.__dict__}")

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
    _logger.log_text(f"api::reversal::body {body.__dict__}")

    try:
        SafaricomUseCase().process_mpesa_reversal(body)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))


@router.post("/callback/reversal", status_code=status.HTTP_201_CREATED)
def callback_reversal(req: ReversalCallbackResult):
    _logger.log_text(f"api::callback_reversal::req {req.__dict__}")

    try:
        safaricom_service.process_reversal_callback(req.Result)
        return {"message": "Record saved successfully"}
    except Exception as ex:
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])
