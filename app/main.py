from fastapi import FastAPI

from app.api.routes import router
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.safaricom_service import SafaricomService

app = FastAPI()

# Mount the API routes
app.include_router(router, prefix="/api")

# Dependency Injection (DI) setup
transaction_repository = FirestoreRepository()
transaction_service = SafaricomService(transaction_repository)


def get_transaction_service():
    return transaction_service


app.dependency_overrides[get_transaction_service] = get_transaction_service
