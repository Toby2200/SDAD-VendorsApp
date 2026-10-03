from database.database import get_connection
import sqlite3

def get_clients_by_vendor(vendor_id, search=""):
    connection = get_connection()

    if search:
        clients = connection.execute(
            """
            SELECT *
            FROM clients
            WHERE vendor_id = ?
            AND name LIKE ?
            LIMIT 25
            """,
            (vendor_id, f"%{search}%")
        ).fetchall()
    else:
        clients = connection.execute(
            """
            SELECT *
            FROM clients
            WHERE vendor_id = ?
            LIMIT 25
            """,
            (vendor_id,)
        ).fetchall()

    connection.close()

    return clients

def get_cart_details(cart):
    if not cart:
        return [], 0.0

    product_ids = [item["product_id"] for item in cart]
    placeholders = ', '.join(['?'] * len(product_ids))

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    products = connection.execute(
        f"""
        SELECT id_product, code, description, price
        FROM products
        WHERE id_product IN ({placeholders})
        """,
        product_ids
    ).fetchall()

    connection.close()

    stock_map = {prod["id_product"]: prod for prod in products}

    detailed_items = []
    grand_total = 0.0

    for item in cart:
        p_id = item["product_id"]
        qty = item["quantity"]

        if p_id in stock_map:
            prod = stock_map[p_id]
            price = prod["price"]
            subtotal = price * qty
            grand_total += subtotal

            detailed_items.append({
                "product_id": p_id,
                "code": prod["code"],
                "description": prod["description"],
                "unit_price": price,
                "quantity": qty,
                "subtotal": subtotal
            })

    return detailed_items, grand_total