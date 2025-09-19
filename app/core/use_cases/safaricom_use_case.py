import json
from dataclasses import asdict

import requests

from app import _logger, app_secret
from app.constants import REVERSAL_RESPONSE_SUCCESS, TRANSACTION_STATUS_RESPONSE
from app.core.entities.safaricom import Reversal
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository
from app.utils import encrypt_initiator_password, get_auth


class SafaricomUseCase:
    def __init__(self):
        self.mpesa_auth_token = get_auth(app_secret['safaricom']['consumer_key'],
                                         app_secret['safaricom']['consumer_secret'])
        self.db = FirestoreRepository()

    def process_mpesa_reversal(self, body: Reversal):
        if not self.mpesa_auth_token:
            print(f'mpesa_auth_token: ++++ {self.mpesa_auth_token}')
            raise Exception("Failed to get auth token")
        else:
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
                    "Amount": str(body.amount),
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
            mpesa_url = app_secret.get('mpesa_url')

            try:
                response = requests.request("POST", f'{mpesa_url}/reversal', headers=headers, json=payload)
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

    def check_transaction_status(self, body: C2BRequest):
        if not self.mpesa_auth_token:
            print(f'mpesa_auth_token: --- {self.mpesa_auth_token}')
            raise Exception("Failed to get auth token")
        else:
            access_token = self.mpesa_auth_token.get('access_token', None)
            api_url = app_secret['safaricom']['transaction_status_url']
            headers = {"Authorization": "Bearer %s" % access_token}

            security_credential = encrypt_initiator_password(app_secret['safaricom']['cert_bucket_name'],
                                                             app_secret['safaricom']['cert_file_name'],
                                                             app_secret['safaricom']['initiator_pass'])

            data = {"Initiator": app_secret['safaricom']['initiator'],
                    "SecurityCredential": security_credential.decode('utf-8'),
                    "CommandID": "TransactionStatusQuery",
                    "TransactionID": body.TransID,
                    "PartyA": app_secret['safaricom']['business_short_code'],
                    "IdentifierType": "4",
                    "ResultURL": "https://mpesa.bigmachini.net/api/callback/transaction_status",
                    "QueueTimeOutURL": app_secret['safaricom']['transaction_status_timeout_callback_url'],
                    "Remarks": body.TransID,
                    "Occasion": json.dumps(body.__dict__)
                    }
            # "ResultURL": app_secret['safaricom']['transaction_status_result_url'],

            payload = {
                "url": api_url,
                "payload": data,
                "auth": {},
                "headers": headers,
                "method_type": "POST"
            }
            mpesa_url = app_secret.get('mpesa_url')
            _logger.log_text(f"SafaricomUseCase::check_transaction_status:: payload --> {payload} url --> {mpesa_url}")
        try:
            response = requests.request("POST", f'{mpesa_url}/transaction_status', headers=headers, json=payload)
            _logger.log_text(f"SafaricomUseCase::check_transaction_status:: response --> {response.json()}")
            if response.status_code == 200:
                res = response.json()
                self.db.save_record({"response": res, "mpesa_code": body.TransID},
                                    TRANSACTION_STATUS_RESPONSE,
                                    res["ConversationID"])

            else:
                raise Exception(f" response --> {response.text}")

        except Exception as ex:
            _logger.log_text(f'SafaricomUseCase::check_transaction_status:: ex --> {ex}')
