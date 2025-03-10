# app/use_cases/airtime_use_case_impl.py
from dataclasses import asdict

import requests

from app import _logger, app_secret
from app.constants import DUPLICATE_TRANSACTION_ERROR, AIRTIME_RESPONSE_SUCCESS, AIRTIME_RESPONSE_FAILED
from app.core.entities.airtime import Airtime
from app.core.interfaces.airtime_use_case import IAirtimeUseCase
from app.core.repositories.firestore_repository import FirestoreRepository
from app.utils import get_signature, get_carrier_info, reverse_airtime


class AirtimeUseCaseKyanda(IAirtimeUseCase):
    def __init__(self):
        self.api_key = app_secret["kyanda"]['api_key']
        self.merchant_id = "kredoh1"
        self.gateway_base_url = app_secret['kyanda']['base_url']
        self.db = FirestoreRepository()

    def buy_airtime(self, airtime: Airtime) -> None:
        _logger.log_text(f"AirtimeUseCaseKyanda:: buy_airtime({airtime})")

        # check if the transactions has already been processed.
        if self.db.get_record("mpesa_code", airtime.mpesa_code, AIRTIME_RESPONSE_SUCCESS):
            raise Exception(DUPLICATE_TRANSACTION_ERROR)
        else:
            headers = {
                "apiKey": self.api_key,
                "Content-Type": "application/json"
            }

            # get telco and formatted number
            telco, phone_number = get_carrier_info(airtime.phone_number)

            # building the signature
            signature = f'{airtime.amount}{phone_number}{telco}{phone_number}{self.merchant_id}'

            # Selecting the correct api based on type of airtime
            if airtime.is_pin_less:
                url = f"{self.gateway_base_url}/billing/v2/airtime/create"
            else:
                url = f"{self.gateway_base_url}/billing/v1/pin-airtime/create"

            hashed_signature = get_signature(signature, self.api_key)

            _logger.log_text(f"AirtimeUseCaseKyanda:: signature {signature}  hashed signature {hashed_signature}")
            # building the payload
            payload = {"MerchantID": self.merchant_id,
                       "phoneNumber": phone_number,
                       "amount": str(airtime.amount),
                       "telco": telco,
                       "initiatorPhone": phone_number,
                       "signature": hashed_signature}

            _logger.log_text(f"AirtimeUseCaseKyanda:: payload {payload}")

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload
                )

                response_json = response.json()
                data = {"airtime_request": asdict(airtime), "payload": payload, "response": response_json,
                        "mpesa_code": airtime.mpesa_code}
                _logger.log_text(f"AirtimeUseCaseKyanda:: data {data}")

                if response.status_code == 200:
                    table_name = AIRTIME_RESPONSE_SUCCESS
                    data['kyanda_ref'] = response_json.get('merchant_reference', None)

                    if response_json.get('status_code', None) not in ["0000", "1100"]:
                        reverse_airtime(airtime.mpesa_code, airtime.amount_paid)
                else:
                    table_name = AIRTIME_RESPONSE_FAILED
                    reverse_airtime(airtime.mpesa_code, airtime.amount_paid)

                self.db.save_record(data, table_name, response_json.get("merchant_reference", None))

            except Exception as ex:
                _logger.log_text(f"AirtimeUseCaseKyanda:: ex {ex.__dict__}")
                _logger.log_text(f"AirtimeUseCaseKyanda:: ex {ex}")
                if "409 Document already exists" not in str(ex):
                    reverse_airtime(airtime.mpesa_code, airtime.amount_paid)