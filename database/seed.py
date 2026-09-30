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

def seed_vendors():
    processed_vendors = prepare_vendor_records(RAW_VENDORS)
    insert_vendors(processed_vendors)
    print("Vendedores de prueba insertados con éxito.")

def seed_clients():
    insert_clients(RAW_CLIENTS)
    print("Clientes de prueba insertados con éxito.")


if __name__ == "__main__":
    seed_vendors()
    seed_clients()