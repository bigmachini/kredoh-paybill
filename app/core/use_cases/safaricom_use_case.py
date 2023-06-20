import os

import requests

from app.core.entities.safaricom import Reversal
from app.core.repositories.firestore_repository import app_secret
from app.utils import encrypt_initiator_password, get_auth


class SafaricomUseCase:
    def __init__(self):
        self.mpesa_auth_token = get_auth(app_secret['safaricom']['consumer_key'],
                                         app_secret['safaricom']['consumer_secret'])

    def process_mpesa_reversal(self, body: Reversal):
        access_token = self.mpesa_auth_token.get('access_token', None)
        api_url = app_secret['safaricom']['reversal_url']
        headers = {"Authorization": "Bearer %s" % access_token}
        security_credential = encrypt_initiator_password(app_secret['safaricom']['cert_bucket_name'],
                                                         app_secret['safaricom']['cert_file_name'],
                                                         app_secret['safaricom']['initiator_pass'])

        data = {"Initiator": app_secret['safaricom']['initiator'],
                "SecurityCredential": security_credential.decode('utf-8'),
                "CommandID": "TransactionReversal",
                "TransactionID": body.mpesa_code,
                "Amount": body.amount,
                "ReceiverParty": app_secret['safaricom']['business_short_code'],
                "RecieverIdentifierType": "11",
                "ResultURL": app_secret['safaricom']['reversal_result_url'],
                "QueueTimeOutURL": app_secret['safaricom']['reversal_timeout_callback_url'],
                "Remarks": "Online Reversal",
                "Occasion": " "
                }

        payload = {
            "url": api_url,
            "payload": data,
            "auth": {},
            "headers": headers,
            "method_type": "POST"
        }
        url = os.getenv('MPESA_URL_V1')
        response = requests.request("POST", f'{url}/reversal', headers=headers, json=payload)
        print("process_mpesa_reversal:: response --> ", response)
