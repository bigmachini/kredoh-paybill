from fastapi import APIRouter, HTTPException, status

from app import _logger
from app.constants import ALLOWED_TELCOS, DUPLICATE_TRANSACTION_ERROR
from app.core.entities.airtime import Airtime
from app.core.entities.kyanda import KyandaIPNRequest
from app.core.entities.safaricom import Reversal, ReversalCallbackResult, TransactionStatusCallbackResult
from app.core.entities.sms import SMS
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.kyanda_service import KyandaService
from app.core.services.safaricom_service import SafaricomService
from app.core.use_cases.bonga_sms_use_case import SMSUseCaseBonga
from app.core.use_cases.kyanda_airtime_use_case import AirtimeUseCaseKyanda
from app.core.use_cases.safaricom_use_case import SafaricomUseCase
from app.utils import get_carrier_info, reverse_airtime, write_to_bucket, delete_file, process_c2b

router = APIRouter()
safaricom_service = SafaricomService(FirestoreRepository())
airtime_services = {"kyanda": AirtimeUseCaseKyanda()}
sms_services = {"bonga": SMSUseCaseBonga()}
db = FirestoreRepository()
callback_services = {"kyanda": KyandaService(db)}


@router.post("/confirmation", status_code=status.HTTP_200_OK)
def create_transaction(transaction: C2BRequest):
    _logger.log_text(f"api::create_transaction:: transaction --> {transaction.__dict__}")
    try:
        carrier = get_carrier_info(transaction.BillRefNumber)
        _logger.log_text(f"api::create_transaction:: carrier --> {carrier}")
        delete_file("kredoh-paybill", f"validation/{transaction.TransID}")
        transaction_data = transaction.dict()
        process_c2b(transaction_data)
        if carrier and carrier[0] in ALLOWED_TELCOS and float(transaction.TransAmount) >= 10 and float(
                transaction.TransAmount) <= 5000:
            safaricom_service.process_c2b(transaction_data)
            return {"message": "Transaction created successfully"}
        else:
            reverse_airtime(transaction.TransID, int(float(transaction.TransAmount)))
    except Exception as ex:
        _logger.log_text(f"api::create_transaction:: ex --> {ex}")
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
    try:
        carrier = get_carrier_info(transaction.BillRefNumber)
        _logger.log_text(f"carrier {carrier}")
        if carrier and carrier[0] in ALLOWED_TELCOS and float(transaction.TransAmount) >= 5 and float(
                transaction.TransAmount) <= 5000:
            write_to_bucket(transaction)
            return {
                "ResultCode": "0",
                "ResultDesc": "Accepted",
            }
        else:
            return {
                "ResultCode": "C2B00011",
                "ResultDesc": "Rejected",
            }
    except Exception as ex:
        _logger.log_text(f"api::validation_api::transaction_data  ex --> {ex}")
        return {
            "ResultCode": "C2B00011",
            "ResultDesc": "Rejected",
        }


@router.post("/callback/kyanda", status_code=status.HTTP_201_CREATED)
def callback_kyanda(req: KyandaIPNRequest):
    _logger.log_text(f"api::callback_kyanda::kyanda_ipn {req.__dict__}")

    try:
        callback_services["kyanda"].process_ipn(req)
        return {"message": "Record saved successfully"}
    except Exception as ex:
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])


@router.post("/send_sms", status_code=status.HTTP_200_OK)
def send_sms(req: SMS):
    _logger.log_text(f"api::send_sms::sms {req.__dict__}")

    try:
        sms_services[req.vendor].send_sms(req)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))


@router.post("/reversal", status_code=status.HTTP_200_OK)
def reversal(req: Reversal):
    _logger.log_text(f"api::reversal::body {req.__dict__}")

    try:
        SafaricomUseCase().process_mpesa_reversal(req)
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


@router.post("/transaction_status", status_code=status.HTTP_200_OK)
def transaction_status(req: C2BRequest):
    _logger.log_text(f"api::transaction_status::req {req.__dict__}")

    try:
        SafaricomUseCase().check_transaction_status(req)
        return {"message": "ok"}
    except Exception as ex:
        if str(ex) == DUPLICATE_TRANSACTION_ERROR:
            raise HTTPException(status_code=400, detail="Duplicate transaction")
        else:
            raise HTTPException(status_code=500, detail=str(ex))


def process_dict(data):
    if 'ResultParameters' in data:
        for param in data['ResultParameters']['ResultParameter']:
            if param.get('Key') == 'OriginatorConversationID' and param.get('Value', None):
                param['Value'] = str(param['Value'])

    return data


@router.post("/callback/transaction_status", status_code=status.HTTP_201_CREATED)
def callback_transaction_status(req: TransactionStatusCallbackResult):
    data = req.__dict__
    _logger.log_text(f"api::callback_transaction_status::req +--------+ {data}")

    try:
        data_result = process_dict(data['Result'])
        _logger.log_text(f"api::callback_transaction_status::data_result +++++ {data_result}")

        safaricom_service.process_transaction_status_callback(data_result)
        return {"message": "Record saved successfully"}
    except Exception as ex:
        _logger.log_text(f"api::callback_transaction_status::ex  +----+++++++----+ {ex}")
        if str(ex).split(":")[0] == "409 Document already exists":
            raise HTTPException(status_code=400, detail="Document already exists")
        else:
            raise HTTPException(status_code=500, detail=str(ex).split(":")[0])
