from database.database import get_connection
from sales import catalog_client

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

def process_cart_for_order(cart_items, vendor_id, client_id):
    if not cart_items:
        return False, "No se seleccionó ningún producto."

    connection = get_connection()
    try:
        client = connection.execute(
            "SELECT * FROM clients WHERE client_id = ? AND vendor_id = ?",
            (client_id, vendor_id)
        ).fetchone()
    finally:
        connection.close()

    if not client:
        return False, "El cliente no existe o no está asociado al vendedor."

    success, result = catalog_client.reserve_stock(cart_items)
    if not success:
        return False, result

    reserved_items = result

    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO orders (vendor_id, client_id, date) VALUES (?, ?, datetime('now'))",
            (vendor_id, client_id),
        )
        order_id = cursor.lastrowid

        for item in reserved_items:
            connection.execute(
                """
                INSERT INTO orderDetails
                (id_order, id_product, code, description, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["product_id"],
                    item["code"],
                    item["description"],
                    item["quantity"],
                    item["unit_price"],
                    item["subtotal"],
                ),
            )
        connection.commit()
        return True, order_id
    except Exception as e:
        connection.rollback()
        catalog_client.release_stock(cart_items)
        raise e
    finally:
        connection.close()