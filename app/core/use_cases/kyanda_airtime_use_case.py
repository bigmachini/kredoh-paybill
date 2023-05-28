# app/use_cases/airtime_use_case_impl.py
import os

import requests

from app.core.entities.airtime import Airtime
from app.core.interfaces.airtime_use_case import IAirtimeUseCase
from app.core.repositories.firestore_repository import FirestoreRepository
from app.utils import get_carrier_info, format_phone_number, get_signature


class AirtimeUseCaseKyanda(IAirtimeUseCase):
    def __init__(self):
        self.api_key = os.getenv('KYANDA_API_KEY')
        self.merchant_id = os.getenv('KYANDA_MERCHANT_ID')
        self.gateway_base_url = os.getenv('KYANDA_BASE_URL')
        self.db = FirestoreRepository()
        print(self.api_key, self.merchant_id, self.gateway_base_url)

    def buy_airtime(self, airtime: Airtime) -> dict:
        print("airtime", airtime)
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json"
        }

        telco = get_carrier_info(airtime.other_phone_number)
        phone_number = format_phone_number(airtime.other_phone_number)
        initiator_phone = format_phone_number(airtime.phone_number)
        signature = f'{airtime.amount}{phone_number}{telco}{initiator_phone}{self.merchant_id}'
        print("signature", signature)

        if airtime.is_pin_less:
            url = f"{self.gateway_base_url}/billing/v1/airtime/create"
        else:
            url = f"{self.gateway_base_url}/billing/v1/pin-airtime/create"

        payload = {
            "MerchantID": self.merchant_id,
            "phoneNumber": phone_number,
            "amount": str(airtime.amount),
            "telco": telco,
            "initiatorPhone": initiator_phone,
            "signature": signature
        }

        print("payload", payload, "url", url)

        payload["signature"] = get_signature(signature, self.api_key)
        print("signature", payload["signature"])

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        response_json = response.json()
        print("response_json", response_json)

        if response.status_code == 200:
            self.db.save_record(response_json, "kyanda.py-airtime-response", response_json.get("transactionId", None))
            return response.json()
        else:
            self.db.save_record(response_json, "kyanda.py-airtime-response-failed",
                                response_json.get("transactionId", None))
            return {"error": "Failed to create airtime"}  # Customize error handling as per your requirements
