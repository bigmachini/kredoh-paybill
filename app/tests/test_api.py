import requests
from fastapi.testclient import TestClient

from app.main import app


def test_create_transaction():
    # Create a test client using the TestClient provided by FastAPI
    client = TestClient(app)

    # Define the request payload
    payload = {
        "TransactionType": "Pay Bill",
        "TransID": "RKTQDM7W6S",
        "TransTime": "20191122063845",
        "TransAmount": "10",
        "BusinessShortCode": "600638",
        "BillRefNumber": "invoice008",
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "hashed",
        "FirstName": "John",
        "MiddleName": "",
        "LastName": "Doe"
    }

    # Send a POST request to the API endpoint
    response = client.post("/transactions", json=payload)

    # Assert that the response status code is 200 (success)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected message
    assert response.json() == {"message": "Transaction created successfully"}
