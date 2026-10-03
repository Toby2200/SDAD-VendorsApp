from flask import Blueprint, render_template, request, session, redirect, url_for

from catalog.service import get_available_products, validate
from auth.decorators import login_required

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/products", methods=["GET", "POST"])
@login_required
def products():
    search_query = request.args.get("search", "").strip()

    if request.method == "POST":
        selected_ids = request.form.getlist("selected_products")

        if not selected_ids:
            return render_template(
                "catalog.html",
                products=get_available_products(search_query=search_query),
                search_query=search_query,
                error="Debes seleccionar al menos un producto para continuar."
            )
        
        cart = []
        for prod_id in selected_ids:
            qty = request.form.get(f"quantity_{prod_id}", type=int, default=1)
            cart.append({"product_id": int(prod_id), "quantity": qty})

        if not validated_cart:
            return render_template(
                "catalog.html",
                products=get_available_products(search_query=search_query),
                search_query=search_query,
                error="Ninguno de los productos seleccionados está disponible en este momento."
                )
        
        
        validated_cart, warnings = validate(cart)

        if warnings:
            print("--> WARNINGS:", warnings)
    
        
        session["cart"] = validated_cart
        return redirect(url_for("sales.cart_summary")) 

    products = get_available_products(search_query=search_query)
    return render_template("catalog.html", products=products, search_query=search_query)