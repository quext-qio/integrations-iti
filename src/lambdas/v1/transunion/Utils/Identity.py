import hashlib
import base64
import binascii
import hmac

def is_verify(body):
    if "Answers" in body:
        return False
    elif "Applicant" in body:
        return True
    else:
        return False

def handle_signature(key, msg):
    key = binascii.unhexlify(key)
    msg = msg.encode()
    return hmac.new(key, msg, hashlib.sha256)

def create_auth_encryption(request, nonce, timestamp, property_id, secret_key):
    m5_request = hashlib.md5(request.encode())
    m5_request = base64.b64encode(m5_request.digest()).decode("utf-8")
    encode_message = property_id + timestamp + nonce + m5_request
    base64_message = base64.b64encode(handle_signature(secret_key.encode("utf-8").hex(), encode_message).digest())
    return base64_message.decode()

def replace_body_content_transunion(response):
    words = {"TransactionStatus": "VerificationStatus", "RiskIndicator": "PotentialRisk"}
    for k in words:
        response = response.replace(k, words[k])
    return response