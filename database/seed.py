from werkzeug.security import generate_password_hash
from database.database import get_connection

RAW_VENDORS = [
    ("Andres", "Befeler", "andres@test.com", "123456", 1),
    ("Maria", "Lopez", "maria@test.com", "abcdef", 1),
    ("Carlos", "Rodriguez", "carlos@test.com", "password123", 0),
]

RAW_CLIENTS = [
    ("Mercadona", "Caleido", "mercadona@test.com", "123456", 1),
    ("Carrefour", "Calle Mayor", "carrefour@test.com", "abcdef", 1),
    ("Walmart", "Avenida Central", "walmart@test.com", "password123", 2)
]

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

def prepare_vendor_records(raw_data):
    return [
        (name, last_name, mail, generate_password_hash(password), active)
        for name, last_name, mail, password, active in raw_data
    ]


def insert_vendors(vendors_data):
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT OR IGNORE INTO vendors
            (name, last_name, mail, password, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            vendors_data
        )
        connection.commit()
    finally:
        connection.close()

def insert_clients(clients_data):
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT OR IGNORE INTO clients
            (name, ubicacion, mail, cedula_juridica, vendor_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            clients_data
        )
        connection.commit()
    finally:
        connection.close()

def insert_products(products_data):
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT OR IGNORE INTO products
            (code, description, quantity, active, price)
            VALUES (?, ?, ?, ?, ?)
            """,
            products_data
        )
        connection.commit()
    finally:
        connection.close()

def seed_vendors():
    processed_vendors = prepare_vendor_records(RAW_VENDORS)
    insert_vendors(processed_vendors)
    print("Vendedores de prueba insertados con éxito.")

def seed_clients():
    insert_clients(RAW_CLIENTS)
    print("Clientes de prueba insertados con éxito.")

def seed_products():
    insert_products(RAW_PRODUCTS)
    print("Productos de prueba insertados con éxito.")


if __name__ == "__main__":
    seed_vendors()
    seed_clients()
    seed_products()