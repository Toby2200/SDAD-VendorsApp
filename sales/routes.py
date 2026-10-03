from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from auth.decorators import login_required
from sales.service import get_cart_details, get_clients_by_vendor, process_cart_for_order

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

@sales_bp.route("/select-clients", methods=["GET", "POST"])
@login_required
def select_clients():

    vendor_id = session.get("vendor_id")

    if request.method == "GET":
        search = request.args.get("search", "").strip()
        clients = get_clients_by_vendor(vendor_id, search)
        return render_template("select_clients.html", clients=clients, search=search)

    selected_client_id = request.form["client_id"]

    session["selected_client_id"] = selected_client_id

    return redirect(url_for("catalog.products"))

@sales_bp.route("/cart_summary", methods=["GET"])
@login_required
def cart_summary():
    session_cart = session.get("cart", [])

    if not session_cart:
        return redirect(url_for("catalog.products"))

    cart_items, grand_total = get_cart_details(session_cart)

    return render_template(
        "cart.html",
        items=cart_items,
        grand_total=grand_total
    )

@sales_bp.route("/cart_summary/checkout", methods=["POST"])
@login_required
def checkout():
    session_cart = session.get("cart", [])

    if not session_cart:
        return jsonify({"error": "El carrito está vacío."}), 400

    cart_items, grand_total = get_cart_details(session_cart)

    if not cart_items:
        return jsonify({"error": "Ninguno de los productos seleccionados está disponible."}), 400

    success, result = process_cart_for_order(
        session_cart,
        vendor_id=session.get("vendor_id"),
        client_id=session.get("selected_client_id")
    )

    if success:
        session.pop("cart", None)
        return render_template("checkout_success.html", sale_id=result)
    else:
        return render_template(
            "cart.html",
            error=result,
            items=get_cart_details(session_cart)[0],
            grand_total=get_cart_details(session_cart)[1]
        )

@sales_bp.route("/checkout_success", methods=["GET"])
@login_required
def checkout_success(order_id):
    return render_template(
        "checkout_success.html", 
        order_id=order_id
    )
