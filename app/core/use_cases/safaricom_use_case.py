import os

import requests

from app.core.repositories.firestore_repository import app_secret
from app.utils import encrypt_initiator_password, get_auth


class SafaricomUseCaseBonga:
    def __init__(self, service_id=''):
        self.mpesa_auth_token = get_auth(app_secret['kredoh-paybill']['safaricom']['consumer_key'],
                                         app_secret['kredoh-paybill']['safaricom']['consumer_secret'])

    def process_mpesa_reversal(self, mpesa_code, amount):
        access_token = self.mpesa_auth_token.get('access_token', None)
        api_url = app_secret['kredoh-paybill']['safaricom']['reversal_url']
        headers = {"Authorization": "Bearer %s" % access_token}
        security_credential = encrypt_initiator_password(app_secret['kredoh-paybill']['safaricom']['cert_bucket_name'],
                                                         app_secret['kredoh-paybill']['safaricom']['cert_file_name'],
                                                         app_secret['kredoh-paybill']['safaricom']['initiator_pass'])

        data = {"Initiator": app_secret['kredoh-paybill']['safaricom']['initiator'],
                "SecurityCredential": security_credential.decode('utf-8'),
                "CommandID": "TransactionReversal",
                "TransactionID": mpesa_code,
                "Amount": amount,
                "ReceiverParty": app_secret['kredoh-paybill']['safaricom']['business_short_code'],
                "RecieverIdentifierType": "11",
                "ResultURL": app_secret['kredoh-paybill']['safaricom']['reversal_result_url'],
                "QueueTimeOutURL": app_secret['kredoh-paybill']['safaricom']['reversal_timeout_callback_url'],
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
        return requests.request("POST", f'{url}/reversal', headers=headers, json=payload)
