from flask import Blueprint, jsonify, request

from catalog.service import get_available_products, get_product_by_ids, reserve_stock, release_stock
#from auth.decorators import login_required

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/products", methods=["GET"])
def list_products():
    search_query = request.args.get("search", "").strip()
    products = get_available_products(search_query=search_query)
    return jsonify([dict(product) for product in products])

@catalog_bp.route("/products/details", methods=["POST"])
def products_details():
    data = request.get_json(silent=True) or {}
    product_ids = data.get("product_ids", [])
    if not isinstance(product_ids, list):
        return jsonify({"error": "product_ids must be a list"}), 400

    if not all(isinstance(pid, int) for pid in product_ids):
        return jsonify({"error": "All product_ids must be integers"}), 400

    return jsonify(get_product_by_ids(product_ids))

def read_items_from_request():
    data = request.get_json(silent=True) or {}
    selected_items = data.get("selected_items", [])
    if not isinstance(selected_items, list):
        return None, jsonify({"error": "selected_items must be a list"}), 400

    for item in selected_items:
        if not isinstance(item, dict) or "product_id" not in item or "quantity" not in item:
            return None, jsonify({"error": "Each item must be a dict with 'product_id' and 'quantity'"}), 400
        if not isinstance(item["product_id"], int) or not isinstance(item["quantity"], int):
            return None, jsonify({"error": "'product_id' and 'quantity' must be integers"}), 400

    return selected_items, None, None

@catalog_bp.route("/products/reserve", methods=["POST"])
def reserve_products():
    selected_items, error_response, status_code = read_items_from_request()
    if error_response:
        return error_response, status_code

    success, result = reserve_stock(selected_items)

    if not success:
        return jsonify({"error": result}), 400
    return jsonify({"items": result}), 200

@catalog_bp.route("/products/release", methods=["POST"])
def release_products():
    selected_items, error_response, status_code = read_items_from_request()
    if error_response:
        return error_response, status_code

    success, result = release_stock(selected_items)
    if not success:
        return jsonify({"error": result}), 400
    return jsonify({"message": "Stock liberado exitosamente."})