from werkzeug.security import generate_password_hash
from database.database import get_connection

# 1. MOCK DATA (Constante desacoplada)
RAW_VENDORS = [
    ("Andres", "Befeler", "andres@test.com", "123456", 1),
    ("Maria", "Lopez", "maria@test.com", "abcdef", 1),
    ("Carlos", "Rodriguez", "carlos@test.com", "password123", 0),
]


# 2. LÓGICA DE NEGOCIO / SEGURIDAD (SRP: Solo procesa contraseñas)
def prepare_vendor_records(raw_data):
    return [
        (name, last_name, mail, generate_password_hash(password), active)
        for name, last_name, mail, password, active in raw_data
    ]


# 3. PERSISTENCIA EN BD (SRP: Solo ejecuta consultas en la base de datos)
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


# 4. ORQUESTADOR (Invocación modular para SDLC / Seed)
def seed_vendors():
    processed_vendors = prepare_vendor_records(RAW_VENDORS)
    insert_vendors(processed_vendors)
    print("Vendedores de prueba insertados con éxito.")


if __name__ == "__main__":
    seed_vendors()