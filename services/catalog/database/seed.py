from database.database import get_connection

RAW_PRODUCTS = [
    ("992831", "Producto A", 10, 1, 10.99),
    ("1233123", "Producto A", 5, 1, 15.99),
    ("23234432 C", "Producto B", 0, 1, 20.99),
    ("4564645 D", "Producto C", 20, 0, 25.99),
    ("5466456 E", "Producto D", 15, 1, 30.99),
    ("6577567 F", "Producto E", 0, 0, 35.99),
    ("7687678 G", "Producto F", 30, 1, 40.99),
    ("8798789 H", "Producto G", 25, 1, 45.99),
    ("9898989 I", "Producto H", 0, 1, 50.99),
    ("10909090 J", "Producto I", 40, 1, 19.99),
]

def insert_products(products_data):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.executemany(
            """
            INSERT INTO products
            (code, description, quantity, active, price)
            VALUES (%s, %s, %s, %s, %s)
            """,
            products_data
        )
        connection.commit()
    finally:
        connection.close()

def seed_products():
    insert_products(RAW_PRODUCTS)
    print("Productos de prueba insertados con éxito.")

def is_table_empty(table_name):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
        return cursor.fetchone()["total"] == 0
    finally:
        connection.close()


def seed_database():
    if is_table_empty("products"):
        seed_products()


if __name__ == "__main__":
    seed_database()