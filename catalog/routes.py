from flask import Blueprint, render_template, request, session, redirect, url_for

from catalog.service import get_available_products, validate
from auth.decorators import login_required

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        selected_ids = request.form.getlist("selected_products")
        
        cart = []
        for prod_id in selected_ids:
            qty = request.form.get(f"quantity_{prod_id}", type=int, default=1)
            cart.append({"product_id": int(prod_id), "quantity": qty})
        
        validated_cart, warnings = validate(cart)

        if warnings:
            print("--> WARNINGS:", warnings)
    
        
        session["cart"] = validated_cart
        return redirect(url_for("sales.cart_summary")) 

    search_query = request.args.get("search")
    products = get_available_products(search_query=search_query)
    return render_template("catalog.html", products=products)