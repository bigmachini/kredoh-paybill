from fastapi import APIRouter, HTTPException

from app.core.entities.airtime import Airtime
from app.core.entities.transaction import C2BRequest
from app.core.services.transaction_service import TransactionService
from app.core.repositories.firestore_repository import FirestoreRepository

router = APIRouter()
transaction_service = TransactionService(FirestoreRepository())


@router.post("/transactions")
def create_transaction(transaction: C2BRequest):
    # Convert the request body to a dictionary
    transaction_data = transaction.dict()

    try:
    # Process the transaction
        transaction_service.process_transaction(transaction_data)

        return {"message": "Transaction created successfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@router.post("/buy_airtime")
def create_transaction(airtime: Airtime):
    # Convert the request body to a dictionary
    transaction_data = transaction.dict()

    # Process the transaction
    firebase_service.process_transaction(transaction_data)

    return {"message": "Transaction created successfully"}


