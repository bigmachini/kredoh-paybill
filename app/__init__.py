import json
import os

from google.cloud import logging, secretmanager

logging_client = logging.Client()

# The name of the log to write to
log_name = "kredoh_paybill_api_onpremise"
# Selects the log to write to
_logger = logging_client.logger(log_name)

secrets = secretmanager.SecretManagerServiceClient()
_name = f"projects/{os.environ.get('PROJECT_ID')}/" \
        f"secrets/{os.environ.get('SECRET_ID')}/" \
        f"versions/{os.environ.get('SECRET_VERSION')}"
app_secret = json.loads(secrets.access_secret_version(request={"name": _name}).payload.data.decode("utf-8"))
