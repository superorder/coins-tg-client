import hmac
import hashlib
import json


def sign(key, message):
    dig = hmac.new(key, json.dumps(message), digestmod=hashlib.sha256)
    return dig.digest()
