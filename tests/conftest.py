"""
conftest.py
-----------
pytest carga este archivo automáticamente ANTES de cualquier test.
Aquí van las "fixtures": funciones que preparan el escenario de cada test.

Objetivo: que cada test empiece SIEMPRE con la misma base de datos
(los datos del seed), sin importar si antes se usó la app o se corrió
otro test. Así un test pasa o falla siempre igual.
"""
import os
import shutil
import sys
import tempfile

import pytest

# Permite hacer "from app import app" aunque pytest se corra desde otra carpeta.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# IMPORTANTE: esto se ejecuta antes de importar app.py.
# Al importar app.py se llama create_app(), que crea la base de datos.
# Al apuntar DATA_DIR a una carpeta temporal, ni siquiera ese primer
# arranque toca tu base de datos real (data/app.db).
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="vendors_test_import_")

from app import app as flask_app  # noqa: E402
from database.database import init_database, DATABASE_FILENAME  # noqa: E402
from database.seed import seed_database  # noqa: E402


@pytest.fixture(scope="session")
def template_database(tmp_path_factory):
    """
    Se ejecuta UNA sola vez por toda la corrida de pytest.
    Crea una base de datos "plantilla" con las tablas y el seed.

    Se hace una sola vez porque generate_password_hash es lento a
    propósito (por seguridad). Después, cada test solo copia el archivo.
    """
    template_dir = tmp_path_factory.mktemp("template_db")
    os.environ["DATA_DIR"] = str(template_dir)

    init_database()
    seed_database()

    return template_dir / DATABASE_FILENAME


@pytest.fixture(autouse=True)
def fresh_database(template_database, tmp_path, monkeypatch):
    """
    autouse=True -> se aplica a TODOS los tests sin tener que pedirla.

    Antes de cada test:
      1. Copia la base de datos plantilla a una carpeta temporal nueva.
      2. Apunta DATA_DIR a esa carpeta, así get_connection() usa esa copia.

    Después del test, pytest borra la carpeta temporal y monkeypatch
    restaura DATA_DIR. El siguiente test vuelve a empezar desde cero.
    """
    shutil.copy(template_database, tmp_path / DATABASE_FILENAME)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    yield


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Navegador simulado, sin sesión (usuario NO logueado)."""
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """Navegador simulado con Andres (vendor_id = 1) ya logueado."""
    with client.session_transaction() as session:
        session["vendor_id"] = 1
    return client