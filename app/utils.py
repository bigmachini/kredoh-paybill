import json
import os
from base64 import b64encode
from typing import Tuple

import phonenumbers
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from phonenumbers import carrier

from app import _logger


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
        _logger.log_text(f"ex {ex}")


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
        url = os.getenv('MPESA_URL_V1')
        r = requests.post(f'{url}/get_auth', data=json.dumps(payload), headers=headers, timeout=30)

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
