from database.database import get_connection


# ------------------------------------------------------------------
# Helpers: funciones pequeñas para no repetir código en cada test
# ------------------------------------------------------------------

def set_session(client, **values):
    with client.session_transaction() as session:
        for key, value in values.items():
            session[key] = value


def get_stock(product_id):
    connection = get_connection()
    row = connection.execute(
        "SELECT quantity FROM products WHERE id_product = ?", (product_id,)
    ).fetchone()
    connection.close()
    return row["quantity"]


def count_orders():
    connection = get_connection()
    total = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    connection.close()
    return total


# ------------------------------------------------------------------
# GET /sales/cart_summary
# ------------------------------------------------------------------

def test_cart_summary_without_cart_redirects_to_catalog(logged_in_client):
    response = logged_in_client.get("/sales/cart_summary")

    assert response.status_code == 302
    assert response.location == "/products"


def test_cart_summary_shows_products_and_total(logged_in_client):
    set_session(logged_in_client, cart=[
        {"product_id": 1, "quantity": 2},  # 2 x 10.99 = 21.98
        {"product_id": 5, "quantity": 1},  # 1 x 30.99 = 30.99
    ])

    response = logged_in_client.get("/sales/cart_summary")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "992831" in html
    assert "5466456 E" in html
    assert "$21.98" in html   # subtotal producto 1
    assert "$52.97" in html   # total = 21.98 + 30.99


# ------------------------------------------------------------------
# POST /sales/cart_summary/checkout
# ------------------------------------------------------------------

def test_checkout_with_empty_cart_returns_400(logged_in_client):
    response = logged_in_client.post("/sales/cart_summary/checkout")

    assert response.status_code == 400
    assert count_orders() == 0


def test_checkout_creates_order_and_reduces_stock(logged_in_client):
    set_session(
        logged_in_client,
        selected_client_id="1",
        cart=[{"product_id": 1, "quantity": 3}],
    )

    response = logged_in_client.post("/sales/cart_summary/checkout")

    assert response.status_code == 200
    assert count_orders() == 1
    assert get_stock(1) == 7  # 10 - 3


def test_checkout_saves_order_details_snapshot(logged_in_client):
    set_session(
        logged_in_client,
        selected_client_id="1",
        cart=[{"product_id": 1, "quantity": 2}],
    )

    logged_in_client.post("/sales/cart_summary/checkout")

    connection = get_connection()
    detail = connection.execute("SELECT * FROM orderDetails").fetchone()
    order = connection.execute("SELECT * FROM orders").fetchone()
    connection.close()

    assert order["vendor_id"] == 1
    assert order["client_id"] == 1
    assert detail["code"] == "992831"
    assert detail["quantity"] == 2
    assert detail["unit_price"] == 10.99
    assert detail["subtotal"] == 21.98


def test_checkout_clears_cart_from_session(logged_in_client):
    set_session(
        logged_in_client,
        selected_client_id="1",
        cart=[{"product_id": 1, "quantity": 1}],
    )

    logged_in_client.post("/sales/cart_summary/checkout")

    with logged_in_client.session_transaction() as session:
        assert "cart" not in session


def test_checkout_with_client_of_other_vendor_is_rejected(logged_in_client):
    # Andres (vendor 1) intenta venderle a Walmart, que es cliente de Maria
    set_session(
        logged_in_client,
        selected_client_id="3",
        cart=[{"product_id": 1, "quantity": 1}],
    )

    logged_in_client.post("/sales/cart_summary/checkout")

    assert count_orders() == 0
    assert get_stock(1) == 10  # el stock NO cambió


def test_checkout_without_selected_client_is_rejected(logged_in_client):
    set_session(logged_in_client, cart=[{"product_id": 1, "quantity": 1}])

    logged_in_client.post("/sales/cart_summary/checkout")

    assert count_orders() == 0


def test_checkout_with_quantity_above_stock_is_rejected(logged_in_client):
    # Simula que alguien manipuló la sesión o que el stock bajó mientras
    # el vendedor armaba el pedido.
    set_session(
        logged_in_client,
        selected_client_id="1",
        cart=[{"product_id": 1, "quantity": 50}],
    )

    logged_in_client.post("/sales/cart_summary/checkout")

    assert count_orders() == 0
    assert get_stock(1) == 10


def test_checkout_failure_keeps_the_cart(logged_in_client):
    set_session(
        logged_in_client,
        selected_client_id="3",  # cliente de otro vendedor -> falla
        cart=[{"product_id": 1, "quantity": 1}],
    )

    logged_in_client.post("/sales/cart_summary/checkout")

    with logged_in_client.session_transaction() as session:
        assert session["cart"] == [{"product_id": 1, "quantity": 1}]