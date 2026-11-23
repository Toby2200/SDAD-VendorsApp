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
from database.seed import seed_database  # noqa: E402


def run_sql(sql, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
    finally:
        connection.close()


def query_one(sql, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        connection.close()


def _product_id(code):
    return query_one("SELECT id_product FROM products WHERE code = %s", (code,))["id_product"]


def _stock_of(code):
    return query_one("SELECT quantity FROM products WHERE code = %s", (code,))["quantity"]


@pytest.fixture(autouse=True)
def fresh_products():
    """Cada test empieza con los 10 productos del seed."""
    run_sql("TRUNCATE TABLE products")
    seed_database()
    yield


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


@pytest.fixture
def auth_headers():
    """Cabecera con un token válido del vendedor 1."""
    return {"Authorization": f"Bearer {create_token(1)}"}


@pytest.fixture
def product_id():
    """product_id("992831") -> id del producto con ese código."""
    return _product_id


@pytest.fixture
def stock_of():
    """stock_of("992831") -> stock actual de ese producto en la base de datos."""
    return _stock_of