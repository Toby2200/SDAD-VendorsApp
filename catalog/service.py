from database.database import get_connection
import sqlite3

def get_available_products():
    connection = get_connection()

    products = connection.execute(
        """
        SELECT *
        FROM products
        WHERE active = 1
        AND quantity > 0
        ORDER BY description ASC
        """
    ).fetchall()

    connection.close()

    return products

def validate(selected_items):
    if not selected_items:
        return [], ["No se seleccionó ningún producto."]

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    validated_cart = []
    warnings = []

    for item in selected_items:
        p_id = item["product_id"]
        requested_qty = max(1, item["quantity"])

        query = "SELECT description, quantity FROM products WHERE id_product = ? AND active = 1"
        prod = connection.execute(query, (p_id,)).fetchone()

        if not prod:
            warnings.append(f"El producto con ID {p_id} ya no está disponible.")
            continue

        available_stock = prod["quantity"]

        if requested_qty > available_stock:
            requested_qty = available_stock
            warnings.append(
                f"La cantidad para '{prod['description']}' superaba el stock ({available_stock}). Se ajustó al máximo disponible."
            )

        validated_cart.append({
            "product_id": p_id,
            "quantity": requested_qty
        })

    connection.close()
    return validated_cart, warnings
