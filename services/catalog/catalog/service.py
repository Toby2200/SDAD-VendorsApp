from database.database import get_connection
import sqlite3

def get_available_products(search_query=None):
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    if search_query:
        # Preparamos el patrón para coincidencia parcial
        search_pattern = f"%{search_query.strip()}%"
        query = """
            SELECT *
            FROM products
            WHERE active = 1
            AND quantity > 0
            AND (code LIKE ? OR description LIKE ?)
            ORDER BY description ASC
        """
        products = connection.execute(query, (search_pattern, search_pattern)).fetchall()
    else: 
        query = """
            SELECT *
            FROM products
            WHERE active = 1
            AND quantity > 0
            ORDER BY description ASC
        """
        products = connection.execute(query).fetchall()

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

def get_product_by_ids(product_ids):
    
    if not product_ids:
        return []

    placeholders = ', '.join('?' for _ in product_ids)

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    query = f"SELECT * FROM products WHERE id_product IN ({placeholders}) AND active = 1"
    product = connection.execute(query, product_ids).fetchall()
    connection.close()
    return [dict(row) for row in product]

def reserve_stock(cart_items):
    connection = get_connection()
    try:
        reserved = []

        for item in cart_items:
            p_id = item["product_id"]
            qty_to_reserve = item["quantity"]

            if qty_to_reserve <= 0:
                raise ValueError(f"La cantidad para el producto con ID {p_id} debe ser mayor que cero.")

            cursor = connection.execute(
                """
                UPDATE products
                SET quantity = quantity - ?
                WHERE id_product = ? AND active = 1 AND quantity >= ?
                """,
                (qty_to_reserve, p_id, qty_to_reserve),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    f"El producto con ID {p_id} no está disponible o no tiene stock suficiente."
                )

            prod = connection.execute(
                "SELECT code, description, price FROM products WHERE id_product = ?",
                (p_id,),
            ).fetchone()

            reserved.append({
                "product_id": p_id,
                "code": prod["code"],
                "description": prod["description"],
                "unit_price": prod["price"],
                "quantity": qty_to_reserve,
                "subtotal": round(prod["price"] * qty_to_reserve, 2),
            })

        connection.commit()
        return True, reserved

    except ValueError as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()

def release_stock(cart_items):
    connection = get_connection()
    try:
        for item in cart_items:
            p_id = item["product_id"]
            qty_to_release = item["quantity"]

            if qty_to_release <= 0:
                raise ValueError(f"La cantidad a liberar para el producto con ID {p_id} debe ser mayor que cero.")

            update_query = "UPDATE products SET quantity = quantity + ? WHERE id_product = ?"

            if update_query == 0:
                raise ValueError(f"No se pudo construir la consulta de actualización para el producto con ID {p_id}.")
            connection.commit()
            return True, None
    except ValueError as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()