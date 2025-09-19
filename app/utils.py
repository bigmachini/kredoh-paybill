import json
from base64 import b64encode
from typing import Tuple

import phonenumbers
import requests
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from google.cloud import storage
from phonenumbers import carrier

from app import _logger, app_secret
from app.constants import REVERSALS
from app.core.entities.transaction import C2BRequest
from app.core.repositories.firestore_repository import FirestoreRepository


def get_carrier_info(phone_number: str) -> [Tuple[str, str], None]:
    phone_number = phone_number.replace(' ', '')
    try:
        ke_number = phonenumbers.parse(phone_number, "KE")
        if ke_number:
            _carrier = carrier.name_for_number(ke_number, "en")
            if _carrier == 'JTL':
                _carrier = 'FAIBA'
            return _carrier.upper(), f"0{ke_number.national_number}"
        else:
            return None
    except phonenumbers.phonenumberutil.NumberParseException as ex:
        _logger.log_text(f"get_carrier_info:: ex {ex}")


def format_phone_number(phone_number):
    return f'0{phone_number[3:]}'


def get_signature(message: str, api_key: str) -> str:
    import hashlib
    import hmac
    message = bytes(message, 'utf-8')
    secret = bytes(api_key, 'utf-8')
    signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
    return signature


def encrypt_initiator_password(bucket_name, cert_file_name, initiator_pass):
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.get_blob(cert_file_name)
        cert_data = blob.download_as_string()

        cert = x509.load_pem_x509_certificate(cert_data)
        pub_key = cert.public_key()

        cipher = pub_key.encrypt(initiator_pass.encode('utf-8'), padding.PKCS1v15())
        return b64encode(cipher)


    except Exception as ex:
        _logger.log_text(f"encrypt_initiator_password:: ex {ex}")
        return False


def get_auth(consumer_key, consumer_secret):
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        headers = {'Content-Type': 'application/json'}
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        payload = {
            "url": url,
            "payload": {},
            "auth": {'consumer_key': consumer_key, 'consumer_secret': consumer_secret},
            "headers": headers,
            "method_type": "GET"
        }
        res = {}
        mpesa_url = app_secret.get('mpesa_url')
        print(f'get_auth: mpesa_url --> {mpesa_url}')
        r = requests.post(f'{mpesa_url}/get_auth', data=json.dumps(payload), headers=headers, timeout=30)
        print(f'get_auth: --- {r}')
        if r.status_code == 200:
            from time import time
            int(time())
            res = r.json()
            res['generated_at'] = int(time())
            res['auth'] = 'auth'
        return res
    except Exception as ex:
        _logger.log_text(f"get_auth:: ex {ex}")
        return {}


def reverse_airtime(mpesa_code: str, amount: int) -> None:
    _logger.log_text(f"reverse_airtime({mpesa_code},{amount})")
    FirestoreRepository().save_record({"amount": str(amount), "mpesa_code": mpesa_code},
                                      REVERSALS, mpesa_code)


def write_to_bucket(c2b: C2BRequest):
    client = storage.Client()
    bucket = client.bucket("kredoh-paybill")
    file_name = f"validation/{c2b.TransID}"
    blob = bucket.blob(file_name)
    blob.upload_from_string(json.dumps(c2b.__dict__))
    _logger.log_text(f'write_to_bucket File {file_name} uploaded to {blob.public_url}')


def delete_file(bucket_name: str, file_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    if blob.exists():
        blob.delete()
        _logger.log_text(f'delete_file File {file_name} deleted from {bucket_name}')


def process_c2b(transaction):
    _logger.log_text(f"api::process_c2b::  transaction --> {transaction}")
    url = "https://erp.kredoh.com/api/v1/kredoh/c2b_transaction"

    payload = json.dumps({
        "TransID": transaction['TransID'],
        "TransAmount": int(float(transaction['TransAmount'])),
        "BusinessShortCode": transaction['BusinessShortCode'],
        "BillRefNumber": transaction['BillRefNumber'],
    })

    headers = {
        'Content-Type': 'application/json',
    }

    _logger.log_text(f"api::process_c2b::  url --> {url} payload --> {payload}")

    response = requests.request("POST", url, headers=headers, data=payload)
    _logger.log_text(f"api::create_transaction::  response --> {response}")
    if response.status_code == 200:
        _logger.log_text(
            f"api::process_c2b:: success response.json() --> {response.json()}")
    else:
        _logger.log_text(
            f"api::process_c2b:: failed response.text --> {response.text}")


x = {'discount': 0.01, 'mpesa_url': 'https://hyj2np9tcp4vvtrkvmte.bigmachini.net',
     'safaricom': {'consumer_key': 'nNm0u8GA3mV00GQeOnaxLwhzfyKIvjTc', 'consumer_secret': 't9GohkGOgGWzAlfL',
                   'business_short_code': '4091221', 'initiator': 'kredoh', 'initiator_pass': 'Z5G!8*hPoTovrU#',
                   'stk_push_url': 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                   'stk_query_url': 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query',
                   'stk_push_call_back_url': 'https://kredoh-api-hjcvzq6kaq-ez.a.run.app/stk_push_callback',
                   'reversal_url': 'https://api.safaricom.co.ke/mpesa/reversal/v1/request',
                   'reversal_result_url': 'https://mpesa.bigmachini.net/api/callback/reversal',
                   'reversal_timeout_callback_url': 'https://mpesa.bigmachini.net/api/callback/reversal',
                   'cert_bucket_name': 'daraja-cert', 'cert_file_name': 'production.cer',
                   'transaction_status_url': 'https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query',
                   'transaction_status_result_url': 'https://mpesa.bigmachini.net/api/callback/transaction_status',
                   'transaction_status_timeout_callback_url': 'https://mpesa.bigmachini.net/api/callback/transaction_status'},
     'bonga_api': {'client_id': 259, 'key': 'EDldQ0GhYvpao35', 'secret': '6hqmVYTKvULfpCYQrRiOXzjZ5NlA2S',
                   'url': 'https://app.bongasms.co.ke/api/vend-pinless-airtime',
                   'vend_pinless_airtime': 'https://app.bongasms.co.ke/api/vend-pinless-airtime',
                   'check_airtime_url': 'https://app.bongasms.co.ke/api/check-airtime-transaction',
                   'url_send_sms': 'https://app.bongasms.co.ke/api/send-sms-v1',
                   'url_prepaid_token': 'https://app.bongasms.co.ke/api/vend-prepaid-token'},
     'kyanda': {'base_url': 'https://api.kyanda.app', 'api_check_balance': '/billing/v1/account-balance',
                'api_transaction_check': '/billing/v1/transaction-check', 'api_airtime': '/billing/v1/airtime/create',
                'api_bill': '/billing/v1/bill/create', 'api_register_callback': '/billing/v1/callback-url/create',
                'api_key': '8203743af7294cea9740dba00dd38189'}}
