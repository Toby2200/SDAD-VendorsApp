from database.database import get_connection

def get_clients_by_vendor(vendor_id):
    connection = get_connection()

    clients = connection.execute(
        """
        SELECT *
        FROM clients
        WHERE vendor_id = ?
        """,
        (vendor_id,)
    ).fetchall()

    connection.close()

    return clients

from database.database import get_connection