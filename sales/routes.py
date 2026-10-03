from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from auth.decorators import login_required
from sales.service import get_cart_details, get_clients_by_vendor

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

@sales_bp.route("/cart-summary", methods=["GET"])
@login_required
def cart_summary():
    session_cart = session.get("cart", [])

    if not session_cart:
        return redirect(url_for("catalog.products"))

    cart_items, grand_total = get_cart_details(session_cart)

    return render_template(
        "cart_summary.html",
        items=cart_items,
        grand_total=grand_total
    )
