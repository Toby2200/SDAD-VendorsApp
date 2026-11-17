from functools import wraps
from flask import g, jsonify, request
from auth.tokens import read_token

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionado."}), 401

        vendor_id = read_token(token.removeprefix("Bearer "))
        if not vendor_id:
            return jsonify({"error": "Token inválido."}), 401

        g.vendor_id = vendor_id

        return function(*args, **kwargs)

    return wrapper