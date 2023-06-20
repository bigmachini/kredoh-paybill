from dataclasses import asdict

import requests

from app.constants import SMS_RESPONSE_SUCCESS, SMS_RESPONSE_FAILED
from app.core.entities.sms import SMS
from app.core.interfaces.sms_use_case import ISMSUseCase
from app.core.repositories.firestore_repository import app_secret, FirestoreRepository


class SMSUseCaseBonga(ISMSUseCase):
    def __init__(self, service_id=''):
        self.api_client_id = app_secret['bonga_api']['client_id']
        self.key = app_secret['bonga_api']['key']
        self.secret = app_secret['bonga_api']['secret']
        self.service_id = service_id
        self.db = FirestoreRepository()
        self.url = "http://167.172.14.50:4002/v1/send-sms"

    def send_sms(self, sms: SMS) -> None:
        print(f"SMSUseCaseBonga:: send_sms({sms})")

        params = {
            "apiClientID": self.api_client_id,
            "key": self.key,
            "secret": self.secret,
            "txtMessage": sms.message,
            "MSISDN": sms.phone_number,
            "serviceID": self.service_id
        }

        try:
            response = requests.post(self.url, params=params)
            response_json = response.json()
            data = {"sms": asdict(sms), "response": response_json}
            print(f"SMSUseCaseBonga:: data", data)

            if response.status_code == 200:
                table_name = SMS_RESPONSE_SUCCESS
                unique_id = f'{response_json.get("unique_id", None)}'
                self.db.save_record(data, table_name, unique_id)
                self.db.update_record(unique_id, "unique_id", unique_id, table_name)
            else:
                table_name = SMS_RESPONSE_FAILED
                self.db.save_record({'failed': response.text}, table_name)


        except Exception as ex:
            print("SMSUseCaseBonga:: ex", ex.__dict__)
            raise Exception(f"Error connecting to Bonga API: {ex}")
