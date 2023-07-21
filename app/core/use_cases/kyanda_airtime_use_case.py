# app/use_cases/airtime_use_case_impl.py
from dataclasses import asdict

import requests

from app import _logger
from app.constants import DUPLICATE_TRANSACTION_ERROR, AIRTIME_RESPONSE_SUCCESS, AIRTIME_RESPONSE_FAILED, C2B_PAYBILL, \
    REVERSALS
from app.core.entities.airtime import Airtime
from app.core.interfaces.airtime_use_case import IAirtimeUseCase
from app.core.repositories.firestore_repository import FirestoreRepository, app_secret
from app.utils import get_signature, get_carrier_info


class AirtimeUseCaseKyanda(IAirtimeUseCase):
    def __init__(self):
        self.api_key = app_secret["kyanda"]['api_key']
        self.merchant_id = "kredoh1"
        self.gateway_base_url = app_secret['kyanda']['base_url']
        self.db = FirestoreRepository()

    def reverse_airtime(self, mpesa_code: str, amount: int) -> None:
        _logger.log_text(f"AirtimeUseCaseKyanda:: reverse_airtime({mpesa_code},{amount})")
        self.db.save_record({"amount": str(amount), "mpesa_code": mpesa_code},
                            REVERSALS, mpesa_code)

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

            # building the payload
            payload = {"MerchantID": self.merchant_id,
                       "phoneNumber": phone_number,
                       "amount": str(airtime.amount),
                       "telco": telco,
                       "initiatorPhone": phone_number,
                       "signature": get_signature(signature, self.api_key)}

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload
                )

                response_json = response.json()
                data = {"airtime_request": asdict(airtime), "payload": payload, "response": response_json,
                        "mpesa_code": airtime.mpesa_code}
                _logger.log_text(f"AirtimeUseCaseKyanda:: data", data)

                if response.status_code == 200:
                    table_name = AIRTIME_RESPONSE_SUCCESS
                    self.db.update_record(airtime.mpesa_code, f'{airtime.vendor}_ref',
                                          response_json.get('merchant_reference'), C2B_PAYBILL)

                    if response_json.get('status_code', None) not in ["0000", "1100"]:
                        self.reverse_airtime(airtime.mpesa_code, airtime.amount_paid)
                else:
                    table_name = AIRTIME_RESPONSE_FAILED
                    self.reverse_airtime(airtime.mpesa_code, airtime.amount_paid)

                self.db.save_record(data, table_name, response_json.get("merchant_reference", None))
                self.db.update_record(airtime.mpesa_code, f'{airtime.vendor}-{table_name}', response_json, C2B_PAYBILL)

            except Exception as ex:
                _logger.log_text("AirtimeUseCaseKyanda:: ex", ex.__dict__)
                _logger.log_text("AirtimeUseCaseKyanda:: ex", ex)
                self.reverse_airtime(airtime.mpesa_code, airtime.amount_paid)
