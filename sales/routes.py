from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from auth.decorators import login_required
from sales.service import get_clients_by_vendor

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

@sales_bp.route("/select-clients", methods=["GET", "POST"])
@login_required
def select_clients():

    vendor_id = session.get("vendor_id")

    if request.method == "GET":
        clients = get_clients_by_vendor(vendor_id)
        return render_template("select_clients.html", clients=clients)

    selected_client_id = request.form["client_id"]

    session["selected_client_id"] = selected_client_id

    return redirect(url_for("catalog.list_products"))