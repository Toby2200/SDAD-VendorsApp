from flask import Blueprint, render_template, request

from catalog.service import get_available_products
from auth.decorators import login_required

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/products", methods=["GET"])
@login_required
def products():
    
    products = get_available_products()
    return render_template("catalog.html", products=products)

    
    