# app/use_cases/airtime_use_case_impl.py
import os

import requests

from app.core.entities.airtime import Airtime
from app.core.interfaces.airtime_use_case import IAirtimeUseCase
from app.utils import get_carrier_info


class AirtimeUseCaseKyanda(IAirtimeUseCase):
    def __init__(self):
        self.api_key = os.getenv('KYANDA_API_KEY')
        self.merchant_id = os.getenv('KYANDA_MERCHANT_ID')
        self.gateway_base_url = os.getenv('KYANDA_BASE_URL')

    def get_signature(self, message: str) -> str:
        import hashlib
        import hmac
        message = bytes(message, 'utf-8')
        secret = bytes(self.api_key, 'utf-8')
        signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def buy_airtime(self, airtime: Airtime) -> dict:
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json"
        }

        telco = get_carrier_info(airtime.other_phone_number)

        payload = {
            "MerchantID": self.merchant_id,
            "phoneNumber": airtime.other_phone_number,
            "amount": airtime.amount,
            "telco": telco,
            "initiatorPhone": airtime.phone_number,
            "signature": self.get_signature(
                f'{airtime.amount}{airtime.other_phone_number}{telco}{airtime.phone_number}{self.merchant_id}')

        }

        response = requests.post(
            f"{self.gateway_base_url}/billing/v1/airtime/create",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to create airtime"}  # Customize error handling as per your requirements
