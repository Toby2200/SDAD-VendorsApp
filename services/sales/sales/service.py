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


def process_cart_for_order(cart, vendor_id, client_id):
    
    if not cart:
        return False, "El carrito está vacío."

    details, grand_total = get_cart_details(cart)

    if not details:
        return False, "Ninguno de los productos seleccionados está disponible."

    connection = get_connection()

    try:

        client = connection.execute(
            "SELECT * FROM clients WHERE client_id = ? AND vendor_id = ?",
            (client_id, vendor_id)
        ).fetchone()
        
        if client is None:
            return False, "El cliente seleccionado no es válido para este vendedor."

        connection.execute(
            "INSERT INTO orders (vendor_id, client_id, date) VALUES (?, ?, datetime('now'))",
            (vendor_id, client_id)
        )

        order_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in details:
            
            product_id = item["product_id"]
            requested_qty = item["quantity"]

            product = connection.execute(
                "SELECT quantity FROM products WHERE id_product = ? AND active = 1",
                (product_id,)
            ).fetchone()

            if product is None:
                raise ValueError(f"El producto con ID {product_id} ya no está disponible.")

            if requested_qty <= 0:
                raise ValueError(f"La cantidad solicitada para el producto con ID {product_id} debe ser mayor que cero.")

            if requested_qty > product["quantity"]:
                raise ValueError(
                    f"La cantidad solicitada para el producto con ID {product_id} supera el stock disponible."
                )

            connection.execute(
                "INSERT INTO orderDetails (id_order, id_product, code, description, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (order_id, item["product_id"], item["code"], item["description"], item["quantity"], item["unit_price"], item["subtotal"])
            )

            connection.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id_product = ? AND active = 1 AND quantity >= ?",
                (item["quantity"], item["product_id"], item["quantity"])
            )

            if connection.total_changes == 0:
                raise ValueError(f"No se pudo actualizar el stock para el producto con ID {product_id}.")

        connection.commit()
        return True, order_id

    except ValueError as ve:
        connection.rollback()
        connection.close()
        return False, str(ve)
    except Exception as e:
        connection.rollback()
        connection.close()
        return False, f"Error al procesar la orden: {str(e)}"
    finally:
        connection.close()