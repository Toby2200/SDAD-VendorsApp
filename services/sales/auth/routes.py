from flask import Blueprint, jsonify, request

from auth.service import authenticate_vendor
from auth.tokens import create_token


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    data = request.get_json(silent=True) or {}
    mail = data.get("mail")
    password = data.get("password")

    if not mail or not password:
        return jsonify({"error": "Se requiere mail y password."}), 400

    vendor = authenticate_vendor(mail, password)

    if vendor is None:
        return jsonify({"error": "Credenciales inválidas."}), 401

    return jsonify({"token": create_token(vendor["vendor_id"]), "vendor": {"name": vendor["name"], "last_name": vendor["last_name"]}}), 200
