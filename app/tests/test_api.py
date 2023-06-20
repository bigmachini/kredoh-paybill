import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_transaction(client):
    transaction_data = {
        "TransactionType": "Pay Bill",
        "TransID": "MPESA000001",
        "TransTime": "20191122063845",
        "TransAmount": "10",
        "BusinessShortCode": "000000",
        "BillRefNumber": "254700000000",
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "254700000000",
        "FirstName": "John",
        "MiddleName": "",
        "LastName": "Doe"
    }
    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Transaction created successfully"}


def test_buy_airtime(client):
    airtime_data = {
        "vendor": "kyanda",
        "amount": 10,
        # Other airtime data...
    }
    response = client.post("/buy_airtime", json=airtime_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Transaction created successfully"}


def test_validation_api(client):
    transaction_data = {
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
    response = client.post("/validate_number", json=transaction_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "ResultCode": "0",
        "ResultDesc": "Accepted",
    }


def test_callback_kyanda(client):
    kyanda_ipn_data = {"category": "UtilityPayment",
                       "source": "PaymentWallet",
                       "destination": "0711000000",
                       "direction": "Outbound",
                       "MerchantID": "kredoh",
                       "details": {"biller_Receipt": "CNKKMZF230528"},
                       "requestMetadata": {},
                       "status": "Success",
                       "status_code": "0000",
                       "message": "Your request has been processed successfully.",
                       "transactionDate": "01-01-2023 00:00 am",
                       "transactionRef": "KREAP0000000",
                       "amount": 150}
    response = client.post("/callback/kyanda", json=kyanda_ipn_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Record saved successfully"}


def test_send_sms(client):
    sms_data = {
        "phone_number": "254700000000",
        "message": "this is a test message",
    }
    response = client.post("/send_sms", json=sms_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Transaction created successfully"}