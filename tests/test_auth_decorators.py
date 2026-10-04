"""
Tests para auth/decorators.py -> login_required

Se prueba de dos formas:
  1. Aislado: una mini app de Flask con una ruta de prueba protegida.
     Así probamos SOLO el decorador, sin depender de catalog ni sales.
  2. En la app real: que TODAS las rutas protegidas estén realmente protegidas.
"""
import pytest
from flask import Flask

from auth.decorators import login_required
from auth.routes import auth_bp


# ------------------------------------------------------------------
# 1. El decorador aislado
# ------------------------------------------------------------------

@pytest.fixture
def mini_client():
    mini_app = Flask(__name__)
    mini_app.config["SECRET_KEY"] = "test"
    # Se registra auth_bp porque el decorador hace url_for("auth.login")
    mini_app.register_blueprint(auth_bp)

    @mini_app.route("/protected")
    @login_required
    def protected():
        return "contenido secreto"

    return mini_app.test_client()


def test_login_required_redirects_when_not_logged_in(mini_client):
    response = mini_client.get("/protected")

    assert response.status_code == 302
    assert response.location == "/login"


def test_login_required_allows_access_when_logged_in(mini_client):
    with mini_client.session_transaction() as session:
        session["vendor_id"] = 1

    response = mini_client.get("/protected")

    assert response.status_code == 200
    assert response.data == b"contenido secreto"


def test_login_required_does_not_run_the_view_when_not_logged_in(mini_client):
    response = mini_client.get("/protected")

    assert b"contenido secreto" not in response.data


def test_login_required_keeps_original_function_name():
    # Gracias a @wraps, Flask sigue viendo el nombre original de la función.
    # Sin @wraps, todas las rutas protegidas se llamarían "wrapper" y
    # Flask daría error al registrar la segunda.
    @login_required
    def my_view():
        return "ok"

    assert my_view.__name__ == "my_view"


# ------------------------------------------------------------------
# 2. Las rutas reales de la app están protegidas
# ------------------------------------------------------------------

@pytest.mark.parametrize("method, url", [
    ("get", "/products"),
    ("post", "/products"),
    ("get", "/sales/select-clients"),
    ("post", "/sales/select-clients"),
    ("get", "/sales/cart_summary"),
    ("post", "/sales/cart_summary/checkout"),
])
def test_protected_routes_redirect_to_login_without_session(client, method, url):
    response = getattr(client, method)(url)

    assert response.status_code == 302
    assert response.location == "/login"