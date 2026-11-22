from database.database import get_connection

def get_available_products(search_query=None):
    connection = get_connection()
    cursor = connection.cursor()
    if search_query:
        # Preparamos el patrón para coincidencia parcial
        search_pattern = f"%{search_query.strip()}%"
        query = """
            SELECT *
            FROM products
            WHERE active = 1
            AND quantity > 0
            AND (code LIKE %s OR description LIKE %s)
            ORDER BY description ASC
        """
        cursor.execute(query, (search_pattern, search_pattern))
    else: 
        query = """
            SELECT *
            FROM products
            WHERE active = 1
            AND quantity > 0
            ORDER BY description ASC
        """
        cursor.execute(query)
    products = cursor.fetchall()

    connection.close()

    # SQL Server devuelve el precio como Decimal; lo pasamos a número para el JSON
    for product in products:
        product["price"] = float(product["price"])
    return products

def get_product_by_ids(product_ids):
    
    if not product_ids:
        return []

    placeholders = ', '.join('%s' for _ in product_ids)

    connection = get_connection()
    cursor = connection.cursor()
    query = f"SELECT * FROM products WHERE id_product IN ({placeholders}) AND active = 1"
    cursor.execute(query, tuple(product_ids))
    product = cursor.fetchall()
    connection.close()

    for row in product:
        row["price"] = float(row["price"])
    return product

def reserve_stock(cart_items):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        reserved = []

        for item in cart_items:
            p_id = item["product_id"]
            qty_to_reserve = item["quantity"]

            if qty_to_reserve <= 0:
                raise ValueError(f"La cantidad para el producto con ID {p_id} debe ser mayor que cero.")

            cursor.execute(
                """
                UPDATE products
                SET quantity = quantity - %s
                WHERE id_product = %s AND active = 1 AND quantity >= %s
                """,
                (qty_to_reserve, p_id, qty_to_reserve),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    f"El producto con ID {p_id} no está disponible o no tiene stock suficiente."
                )

            cursor.execute(
                "SELECT code, description, price FROM products WHERE id_product = %s",
                (p_id,),
            )
            prod = cursor.fetchone()
            price = float(prod["price"])

            reserved.append({
                "product_id": p_id,
                "code": prod["code"],
                "description": prod["description"],
                "unit_price": price,
                "quantity": qty_to_reserve,
                "subtotal": round(price * qty_to_reserve, 2),
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
    cursor = connection.cursor()
    try:
        for item in cart_items:
            p_id = item["product_id"]
            qty_to_release = item["quantity"]

            if qty_to_release <= 0:
                raise ValueError(f"La cantidad a liberar para el producto con ID {p_id} debe ser mayor que cero.")

            update_query = "UPDATE products SET quantity = quantity + %s WHERE id_product = %s"
            cursor.execute(update_query, (qty_to_release, p_id))

            if cursor.rowcount == 0:
                raise ValueError(f"El producto con ID {p_id} no existe.")

        connection.commit()
        return True, None
    except ValueError as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()