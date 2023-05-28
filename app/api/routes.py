from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.services.transaction_service import TransactionServiceImpl
from app.core.repositories.firestore_repository import FirestoreRepository

router = APIRouter()
transaction_service = TransactionServiceImpl(FirestoreRepository())

# Define the request body model
class TransactionRequest(BaseModel):
    TransactionType: str
    TransID: str
    TransTime: str
    TransAmount: str
    BusinessShortCode: str
    BillRefNumber: str
    InvoiceNumber: str
    OrgAccountBalance: str
    ThirdPartyTransID: str
    MSISDN: str
    FirstName: str
    MiddleName: str
    LastName: str


@router.post("/transactions")
def create_transaction(transaction: TransactionRequest):
    # Convert the request body to a dictionary
    transaction_data = transaction.dict()

    # Process the transaction
    transaction_service.process_transaction(transaction_data)

    return {"message": "Transaction created successfully"}
