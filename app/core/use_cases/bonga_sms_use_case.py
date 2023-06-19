from dataclasses import asdict

import requests

from app.constants import SMS_RESPONSE_SUCCESS, SMS_RESPONSE_FAILED
from app.core.entities.sms import SMS
from app.core.interfaces.sms_use_case import ISMSUseCase
from app.core.repositories.firestore_repository import app_secret, FirestoreRepository


class SMSUseCaseBonga(ISMSUseCase):
    def __init__(self, service_id=4889):
        self.api_client_id = app_secret['bonga_api']['client_id']
        self.key = app_secret['bonga_api']['key'],
        self.secret = app_secret['bonga_api']['secret']
        self.service_id = service_id
        self.db = FirestoreRepository()

    def send_sms(self, sms: SMS) -> None:
        print(f"SMSUseCaseBonga:: send_sms({sms})")

        payload = {
            "apiClientID": self.api_client_id,
            "key": self.key,
            "secret": self.secret,
            "txtMessage": sms.message,
            "MSISDN": sms.phone_number,
            "serviceID": self.service_id
        }

        headers = {}
        url = app_secret['bonga_api']['url_send_sms']

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )

            response_json = response.json()
            data = {"sms": asdict(sms), "payload": payload, "response": response_json}
            print(f"AirtimeUseCaseKyanda:: data", data)

            if response.status_code == 200:
                status = response.get('status', None)
                table_name = SMS_RESPONSE_SUCCESS
            else:
                table_name = SMS_RESPONSE_FAILED

            self.db.save_record(data, table_name, response_json.get("merchant_reference", None))

        except Exception as ex:
            print("ex", ex.__dict__)
            raise Exception(f"Error connecting to Bonga API: {ex}")
