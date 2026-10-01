from database.database import get_connection

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