import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if not os.getenv("DATABASE_URL"):
    pytest.exit("Set DATABASE_URL to a test database before running the tests.", returncode=2)

os.environ.setdefault("TOKEN_SECRET", "test-token-secret")

from app import app as flask_app  # noqa: E402  (create_app aplica las migraciones)
from auth.tokens import create_token  # noqa: E402
from database.database import get_connection  # noqa: E402
from database.seed import RAW_CLIENTS, RAW_VENDORS, insert_clients, insert_vendors, prepare_vendor_records  # noqa: E402

from tests.data import ANDRES  # noqa: E402

# Hashear contraseñas es lento a propósito, así que se hace una sola vez.
HASHED_VENDORS = prepare_vendor_records(RAW_VENDORS)

def run_sql(sql, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
    finally:
        connection.close()


def query_all(sql, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        connection.close()


@pytest.fixture(autouse=True)
def fresh_database():
    """Cada test empieza con 3 vendedores, 3 clientes y ningún pedido."""
    run_sql("DELETE FROM orderDetails")
    run_sql("DELETE FROM orders")
    run_sql("DELETE FROM clients")
    run_sql("DELETE FROM vendors")
    run_sql("DBCC CHECKIDENT ('vendors', RESEED, 0)")
    run_sql("DBCC CHECKIDENT ('clients', RESEED, 0)")
    insert_vendors(HASHED_VENDORS)
    insert_clients(RAW_CLIENTS)
    yield


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


@pytest.fixture
def token():
    """Token válido de Andres."""
    return create_token(ANDRES)


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db_rows():
    """db_rows("SELECT ...") -> filas de la base de datos de sales."""
    return query_all