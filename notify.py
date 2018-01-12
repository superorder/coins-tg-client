from requests import post
from os import environ
from crypto_utils import sign

from logging_utils import get_module_logger

IPN_URL = environ.get('TG_IPN_URL')
IPN_SECRET = environ.get('TG_IPN_SECRET')

logger = get_module_logger(__name__)


def notify(message, sender):
    data = {
        "message": message,
        "sender": sender,
    }
    hmac = sign(IPN_SECRET, data)
    logger.info("Going to send notification: %s (hmac: %s)", str(data), hmac)

    try:
      response = post(IPN_URL, json=data, headers={'hmac': hmac})
      logger.info("Response: %d", response.status_code)

    except Exception as exception:
        logger.error(exception)
