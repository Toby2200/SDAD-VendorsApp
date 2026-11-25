from database.database import get_connection
from sales import catalog_client

def get_clients_by_vendor(vendor_id, search=""):
    connection = get_connection()
    cursor = connection.cursor()

    if search:
        cursor.execute(
             """
            SELECT TOP 25 *
            FROM clients
            WHERE vendor_id = %s
            AND active = 1
            AND name LIKE %s
            """,
            (vendor_id, f"%{search}%")
        )
        clients = cursor.fetchall()
    else:
        cursor.execute(
            """
            SELECT TOP 25 *
            FROM clients
            WHERE vendor_id = %s
            AND active = 1
            """,
            (vendor_id,)
        )
        clients = cursor.fetchall()

    connection.close()

    return clients

def process_cart_for_order(cart_items, vendor_id, client_id, token):
    if not cart_items:
        return False, "No se seleccionó ningún producto."

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM clients WHERE client_id = %s AND vendor_id = %s AND active = 1",
            (client_id, vendor_id)
        )
        client = cursor.fetchone()
    finally:
        connection.close()

    if not client:
        return False, "El cliente no existe o no está asociado al vendedor."

    success, result = catalog_client.reserve_stock(cart_items, token)
    if not success:
        return False, result

    reserved_items = result

    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO orders (vendor_id, client_id, [date]) OUTPUT INSERTED.id_order VALUES (%s, %s, SYSUTCDATETIME())",
            (vendor_id, client_id),
        )
        order_id = cursor.fetchone()["id_order"]

        for item in reserved_items:
            cursor.execute(
                """
                INSERT INTO orderDetails
                (id_order, id_product, code, description, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        catalog_client.release_stock(cart_items, token)
        raise e
    finally:
        connection.close()