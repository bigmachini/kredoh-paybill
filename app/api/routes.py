from fastapi import APIRouter, HTTPException, status

from app.constants import ALLOWED_TELCOS
from app.core.entities.airtime import Airtime
from app.core.entities.kyanda import KyandaIPNRequest
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.kyanda_service import KyandaService
from app.core.services.transaction_service import TransactionService
from app.core.use_cases.kyanda_airtime_use_case import AirtimeUseCaseKyanda
from app.utils import get_carrier_info

router = APIRouter()
transaction_service = TransactionService(FirestoreRepository())
airtime_services = {"kyanda": AirtimeUseCaseKyanda()}

db = FirestoreRepository()
callback_services = {"kyanda": KyandaService(db)}


@router.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: C2BRequest):
    # Convert the request body to a dictionary
    transaction_data = transaction.dict()

    try:
        # Process the transaction
        transaction_service.process_transaction(transaction_data)
        return {"message": "Transaction created successfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/buy_airtime", status_code=status.HTTP_200_OK)
def buy_airtime(airtime: Airtime):
    airtime_services[airtime.vendor].buy_airtime(airtime)
    return {"message": "Transaction created successfully"}


@router.post("/validate_number", status_code=status.HTTP_200_OK)
def validation_api(transaction: C2BRequest):
    carrier = get_carrier_info(transaction.BillRefNumber)
    print("carrier", carrier)
    if carrier in ALLOWED_TELCOS:
        return {
            "ResultCode": "0",
            "ResultDesc": "Accepted",
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid number")


@router.post("/callback/kyanda", status_code=status.HTTP_201_CREATED)
def callback_kyanda(kyanda_ipn: KyandaIPNRequest):
    response = callback_services["kyanda"].process_ipn(kyanda_ipn)
    print("response", response)
    return {"message": "Record saved successfully"}
