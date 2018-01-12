from hmac import new
from hashlib import sha512
from json import dumps


def sign(key, message):
    key_bytes = key.encode()
    message_bytes = dumps(message).encode()
    dig = new(key_bytes, message_bytes, digestmod=sha512)
    return dig.hexdigest()
