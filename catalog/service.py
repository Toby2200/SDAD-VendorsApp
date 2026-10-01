from database.database import get_connection

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