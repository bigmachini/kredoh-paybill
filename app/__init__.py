from google.cloud import logging

logging_client = logging.Client()

# The name of the log to write to
log_name = "kredoh_paybill_api_onpremise"
# Selects the log to write to
_logger = logging_client.logger(log_name)
