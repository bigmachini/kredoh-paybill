import os
from dataclasses import asdict

import requests

from app import _logger
from app.constants import REVERSAL_RESPONSE_SUCCESS
from app.core.entities.safaricom import Reversal
from app.core.repositories.firestore_repository import app_secret, FirestoreRepository
from app.utils import encrypt_initiator_password, get_auth


class SafaricomUseCase:
    def __init__(self):
        self.mpesa_auth_token = get_auth(app_secret['safaricom']['consumer_key'],
                                         app_secret['safaricom']['consumer_secret'])
        self.db = FirestoreRepository()

    def process_mpesa_reversal(self, body: Reversal):
        if not self.mpesa_auth_token:
            raise Exception("Failed to get auth token")

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

        try:
            response = requests.request("POST", f'{url}/reversal', headers=headers, json=payload)
            _logger.log_text(f"SafaricomUseCase::process_mpesa_reversal:: response --> {response.json()}")

            if response.status_code == 200:
                table_name = REVERSAL_RESPONSE_SUCCESS
                res = response.json()
                self.db.save_record({"request": asdict(body), "response": res, "mpesa_code": body.mpesa_code},
                                    table_name,
                                    body.mpesa_code)
            else:
                raise Exception(f" response --> {response.text}")

        except Exception as ex:
            _logger.log_text(f"SafaricomUseCase::process_mpesa_reversal:: ex {ex.__dict__}")
            raise Exception(f"{ex}")

    def check_transaction_status(self, mpesa_code: str, store_number: str):
        if not self.mpesa_auth_token:
            raise Exception("Failed to get auth token")
        else:
            access_token = self.mpesa_auth_token.get('access_token', None)
            api_url = "https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query"
            headers = {"Authorization": "Bearer %s" % access_token}

            security_credential = encrypt_initiator_password(app_secret['cert_bucket_name'],
                                                             app_secret['cert_file_name'],
                                                             app_secret['initiator_pass'])
            data = {"Initiator": app_secret['initiator'],
                    "SecurityCredential": security_credential.decode('utf-8'),
                    "CommandID": "TransactionStatusQuery",
                    "TransactionID": mpesa_code,
                    "PartyA": store_number,
                    "IdentifierType": "4",
                    "ResultURL": "https://kredoh-api-hjcvzq6kaq-ez.a.run.app/transaction_status_callback",
                    "QueueTimeOutURL": "https://kredoh-api-hjcvzq6kaq-ez.a.run.app/transaction_status_callback",
                    "Remarks": mpesa_code,
                    "Occasion": mpesa_code
                    }

            payload = {
                "url": api_url,
                "payload": data,
                "auth": {},
                "headers": headers,
                "method_type": "POST"
            }
            url = os.getenv('MPESA_URL_V1')
            _logger.log_text(f"SafaricomUseCase::check_transaction_status:: payload --> {payload} url --> {url}")
        try:
            response = requests.request("POST", f'{url}/transaction_status', headers=headers, json=payload)
            response_text = response.text.replace('\n', '').replace(' ', '')
            _logger.log_text(
                f"SafaricomUseCase::check_transaction_status:: status_code --> {response.status_code}  response_text --> {response_text}")

            vals = {'status_code': response.status_code, 'response_text': response_text}

            if response.status_code == 200:
                vals = response.json()
            else:
                raise Exception(f"Failed to get auth token:: {response_text}")

        except Exception as ex:
            _logger.log_text(f'SafaricomUseCase::check_transaction_status:: ex --> {ex}')
