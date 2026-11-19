from flask import Blueprint, g, jsonify, request
from auth.decorators import login_required
from sales.service import  get_clients_by_vendor, process_cart_for_order
from sales.catalog_client import CatalogUnavailable

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

@sales_bp.route("/clients", methods=["GET"])
@login_required
def list_clients():
    search = request.args.get("search", "").strip()
    clients = get_clients_by_vendor(g.vendor_id, search)
    return jsonify([dict(client) for client in clients])

@sales_bp.route("/orders", methods=["POST"])
@login_required
def create_order():
    vendor_id = g.vendor_id
    token = request.headers["Authorization"].removeprefix("Bearer ")
    data = request.get_json(silent=True) or {}
    client_id = data.get("client_id")
    cart_items = data.get("cart_items")

    # 1. Revisar que el body tenga el formato correcto
    if not isinstance(client_id, int) or not isinstance(cart_items, list) or not cart_items:
        return jsonify({"error": "Se requiere client_id (entero) y cart_items (lista no vacía)."}), 400

    # 2. Intentar crear el pedido; si catalog está caído, responder 503
    try:
        success, result = process_cart_for_order(cart_items, vendor_id, client_id, token)
    except CatalogUnavailable:
        return jsonify({
            "error": "El catálogo no está disponible en este momento. Inténtalo de nuevo en unos minutos."
        }), 503

    # 3. Si no se pudo (sin stock, cliente ajeno), responder 409
    if not success:
        return jsonify({"error": result}), 409

    # 4. Todo bien: devolver el número de pedido
    return jsonify({"order_id": result}), 201