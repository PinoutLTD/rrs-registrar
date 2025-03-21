import jwt
from flask import request, jsonify
from dotenv import load_dotenv
import os
from functools import wraps
import datetime

load_dotenv()
SHARED_SECRET = os.getenv("SHARED_SECRET")
PP_PAYLOAD = "Payment Provider"
PRS_PAYLOAD = "PRS"

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SHARED_SECRET, algorithms=["HS256"])
        
        if payload.get('app') != PP_PAYLOAD:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')   
        print(token)
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        token = token.split(" ")[1]
        payload = verify_jwt(token)
        
        if not payload:
            return jsonify({"error": "Invalid service or token"}), 403
        
        request.payload = payload
        return f(*args, **kwargs)
    return decorated_function


def generate_token():
    payload = {
        "service": PRS_PAYLOAD,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    token = jwt.encode(payload, SHARED_SECRET, algorithm="HS256")
    return token