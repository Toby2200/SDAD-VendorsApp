"""
Tests para catalog/routes.py -> /products

Datos del seed que usamos (siempre iguales gracias a conftest.py):
  id 1 -> "992831"     Producto A  stock 10  activo
  id 2 -> "1233123"    Producto A  stock 5   activo
  id 3 -> "23234432 C" Producto B  stock 0   activo   (sin stock)
  id 4 -> "4564645 D"  Producto C  stock 20  INACTIVO
  id 5 -> "5466456 E"  Producto D  stock 15  activo
"""


# ------------------------------------------------------------------
# GET /products
# ------------------------------------------------------------------

def test_products_page_loads_when_logged_in(logged_in_client):
    response = logged_in_client.get("/products")

    assert response.status_code == 200


def test_products_page_shows_only_active_products_with_stock(logged_in_client):
    response = logged_in_client.get("/products")
    html = response.get_data(as_text=True)

    assert "992831" in html          # activo y con stock
    assert "5466456 E" in html       # activo y con stock
    assert "23234432 C" not in html  # sin stock
    assert "4564645 D" not in html   # inactivo


def test_products_search_filters_by_code(logged_in_client):
    response = logged_in_client.get("/products?search=9928")
    html = response.get_data(as_text=True)

    assert "992831" in html
    assert "5466456 E" not in html


def test_products_search_filters_by_description(logged_in_client):
    response = logged_in_client.get("/products?search=Producto D")
    html = response.get_data(as_text=True)

    assert "5466456 E" in html
    assert "992831" not in html


# ------------------------------------------------------------------
# POST /products (elegir productos para el carrito)
# ------------------------------------------------------------------

def test_select_products_saves_cart_and_redirects(logged_in_client):
    response = logged_in_client.post("/products", data={
        "selected_products": ["1", "5"],
        "quantity_1": "3",
        "quantity_5": "2",
    })

    assert response.status_code == 302
    assert response.location == "/sales/cart_summary"

    with logged_in_client.session_transaction() as session:
        assert session["cart"] == [
            {"product_id": 1, "quantity": 3},
            {"product_id": 5, "quantity": 2},
        ]


def test_select_products_without_selection_does_not_create_cart(logged_in_client):
    response = logged_in_client.post("/products", data={})

    assert response.status_code == 200  # se queda en el catálogo
    with logged_in_client.session_transaction() as session:
        assert "cart" not in session


def test_select_products_quantity_above_stock_is_adjusted(logged_in_client):
    # El producto 1 solo tiene 10 en stock
    logged_in_client.post("/products", data={
        "selected_products": ["1"],
        "quantity_1": "50",
    })

    with logged_in_client.session_transaction() as session:
        assert session["cart"] == [{"product_id": 1, "quantity": 10}]


def test_select_products_quantity_zero_is_adjusted_to_one(logged_in_client):
    logged_in_client.post("/products", data={
        "selected_products": ["1"],
        "quantity_1": "0",
    })

    with logged_in_client.session_transaction() as session:
        assert session["cart"] == [{"product_id": 1, "quantity": 1}]


def test_select_only_inactive_product_does_not_create_cart(logged_in_client):
    # El producto 4 está inactivo: aunque alguien lo mande a mano en el
    # formulario, no debe entrar al carrito.
    response = logged_in_client.post("/products", data={
        "selected_products": ["4"],
        "quantity_4": "1",
    })

    assert response.status_code == 200
    with logged_in_client.session_transaction() as session:
        assert "cart" not in session


def test_select_mixed_products_keeps_only_available_ones(logged_in_client):
    logged_in_client.post("/products", data={
        "selected_products": ["1", "4"],
        "quantity_1": "2",
        "quantity_4": "2",
    })

    with logged_in_client.session_transaction() as session:
        assert session["cart"] == [{"product_id": 1, "quantity": 2}]