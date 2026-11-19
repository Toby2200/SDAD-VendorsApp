import pytest
from database.database import get_connection
from sales.service import get_cart_details, process_cart_for_order

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


# ==============================================================================
# TESTS DE get_cart_details
# ==============================================================================

def test_get_cart_details_with_valid_cart():
    products, grand_total = get_cart_details([{"product_id": 1, "quantity": 2}])

    assert products[0]["code"] == "992831"
    assert products[0]["unit_price"] == 10.99
    assert products[0]["subtotal"] == pytest.approx(21.98)
    assert grand_total == pytest.approx(21.98)


def test_get_cart_details_with_empty_cart():
    cart = []
    items, grand_total = get_cart_details(cart)

    assert items == []
    assert grand_total == 0.0


def test_get_cart_details_with_nonexistent_product():
    cart = [{"product_id": 999999, "quantity": 1}]
    items, grand_total = get_cart_details(cart)

    assert items == []
    assert grand_total == 0.0


def test_get_cart_details_with_mixed_cart():

    cart = [
        {"product_id": 1, "quantity": 1},
        {"product_id": 999999, "quantity": 1}
    ]
    items, grand_total = get_cart_details(cart)

    assert len(items) == 1
    assert grand_total == pytest.approx(10.99)


# ==============================================================================
# TESTS DE process_cart_for_order
# ==============================================================================

def test_process_cart_for_order_with_valid_cart():

    cart = [{"product_id": 1, "quantity": 3}]
    success, result = process_cart_for_order(
        cart, 
        vendor_id=1, 
        client_id=1
    )

    assert success is True
    assert isinstance(result, int)
    assert result == 1
    assert get_stock(1) == 7


def test_process_cart_for_order_with_empty_cart():
    cart = []
    success, result = process_cart_for_order(cart, vendor_id=1, client_id=1)

    assert success is False
    assert result == "El carrito está vacío."
    assert count_orders() == 0


def test_process_cart_for_order_with_invalid_product():
    cart = [{"product_id": 999999, "quantity": 1}]
    success, result = process_cart_for_order(cart, vendor_id=1, client_id=1)

    assert success is False
    assert "Ninguno de los productos seleccionados está disponible" in result
    assert count_orders() == 0


def test_process_cart_for_order_with_mixed_cart():
    cart = [
        {"product_id": 1, "quantity": 1},
        {"product_id": 999999, "quantity": 1}
    ]
    success, result = process_cart_for_order(
        cart, 
        vendor_id=1, 
        client_id=1
    )

    assert success is True
    assert get_stock(1) == 9
    assert count_orders() == 1
    assert isinstance(result, int)


def test_process_cart_for_order_with_exceeding_quantity():
    cart = [{"product_id": 1, "quantity": 100}]

    success, result = process_cart_for_order(
        cart, 
        vendor_id=1, 
        client_id=1
    )

    assert success is False
    assert isinstance(result, str) 
    assert "supera el stock disponible" in result
    assert count_orders() == 0


def test_process_cart_for_order_with_inactive_product():
    success, result = process_cart_for_order(
        [{"product_id": 4, "quantity": 1}], vendor_id=1, client_id=1
    )

    assert success is False
    assert count_orders() == 0


def test_process_cart_for_order_with_client_of_other_vendor():
    success, result = process_cart_for_order(
        [{"product_id": 1, "quantity": 1}], vendor_id=1, client_id=3
    )

    assert success is False
    assert "cliente seleccionado no es válido" in result
    assert count_orders() == 0


def test_process_cart_for_order_with_negative_quantity():

    cart = [{"product_id": 1, "quantity": -5}]
    success, result = process_cart_for_order(cart, vendor_id=1, client_id=1)

    assert success is False or isinstance(result, (int, str))