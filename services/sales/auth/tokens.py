import os
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_SECRET = os.getenv("TOKEN_SECRET", "dev-token-secret")
TOKEN_MAX_AGE_S = int(os.getenv("TOKEN_MAX_AGE_S", "28800"))   # 8 horas

_serializer = URLSafeTimedSerializer(TOKEN_SECRET, salt="vendor-auth")

def create_token(vendor_id):
    return _serializer.dumps({"vendor_id": vendor_id})

def read_token(token):
    try:
        data = _serializer.loads(token, max_age=TOKEN_MAX_AGE_S)
        return data["vendor_id"]
    except (BadSignature, SignatureExpired):
        return None

