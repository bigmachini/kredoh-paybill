from fastapi import FastAPI

from app.api.routes import router
from app.core.repositories.firestore_repository import FirestoreRepository
from app.core.services.transaction_service import TransactionServiceImpl

app = FastAPI()

# Mount the API routes
app.include_router(router, prefix="/api")

# Dependency Injection (DI) setup
transaction_repository = FirestoreRepository()
transaction_service = TransactionServiceImpl(transaction_repository)

# Register the transaction service as a dependency
def get_transaction_service():
    return transaction_service

app.dependency_overrides[get_transaction_service] = get_transaction_service

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
