import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
DATABASE_FILENAME = "app.db"


def get_database_path():
    data_dir = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
    return os.path.join(data_dir, DATABASE_FILENAME)


def get_connection():
    database_path = get_database_path()

    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    connection = sqlite3.connect(database_path)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection

def init_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            mail TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ubicacion TEXT,
            mail TEXT,
            cedula_juridica TEXT,
            vendor_id INTEGER NOT NULL,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id_order INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orderDetails (
            id_orderDetail INTEGER PRIMARY KEY AUTOINCREMENT,
            id_order INTEGER NOT NULL,
            id_product INTEGER NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_order) REFERENCES orders(id_order),
            FOREIGN KEY (id_product) REFERENCES products(id_product)
        )
    """)

    connection.commit()
    connection.close()