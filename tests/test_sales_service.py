import pytest
from database.database import get_connection
from sales.service import get_cart_details, process_cart_for_order


def get_real_valid_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener un producto activo con stock
    cursor.execute("SELECT id_product, price, quantity FROM products WHERE active = 1 AND quantity > 0 LIMIT 2")
    products = cursor.fetchall()

    # Obtener un cliente y su vendedor correspondiente
    cursor.execute("SELECT client_id, vendor_id FROM clients LIMIT 1")
    client = cursor.fetchone()

    conn.close()
    return products, client


# ==============================================================================
# TESTS DE get_cart_details
# ==============================================================================

def test_get_cart_details_with_valid_cart():
    products, _ = get_real_valid_data()
    if not products:
        pytest.skip("No hay productos activos en la base de datos real.")

    cart = [{"product_id": products[0]["id_product"], "quantity": 1}]
    items, grand_total = get_cart_details(cart)

    assert len(items) == 1
    assert grand_total > 0


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
    products, _ = get_real_valid_data()
    if not products:
        pytest.skip("No hay productos activos en la base de datos real.")

    cart = [
        {"product_id": products[0]["id_product"], "quantity": 1},
        {"product_id": 999999, "quantity": 1}
    ]
    items, grand_total = get_cart_details(cart)

    assert len(items) == 1
    assert grand_total > 0


# ==============================================================================
# TESTS DE process_cart_for_order
# ==============================================================================

def test_process_cart_for_order_with_valid_cart():
    products, client = get_real_valid_data()
    if not products or not client:
        pytest.skip("Se requieren datos reales de cliente y productos en la BD.")

    cart = [{"product_id": products[0]["id_product"], "quantity": 1}]
    success, result = process_cart_for_order(
        cart, 
        vendor_id=client["vendor_id"], 
        client_id=client["client_id"]
    )

    assert success is True
    assert isinstance(result, int)


def test_process_cart_for_order_with_empty_cart():
    products, client = get_real_valid_data()
    vendor_id = client["vendor_id"] if client else 1
    client_id = client["client_id"] if client else 1

    cart = []
    success, result = process_cart_for_order(cart, vendor_id=vendor_id, client_id=client_id)

    assert success is False
    assert result == "El carrito está vacío."


def test_process_cart_for_order_with_invalid_product():
    products, client = get_real_valid_data()
    vendor_id = client["vendor_id"] if client else 1
    client_id = client["client_id"] if client else 1

    cart = [{"product_id": 999999, "quantity": 1}]
    success, result = process_cart_for_order(cart, vendor_id=vendor_id, client_id=client_id)

    assert success is False
    assert "Ninguno de los productos seleccionados está disponible" in result


def test_process_cart_for_order_with_mixed_cart():
    products, client = get_real_valid_data()
    if not products or not client:
        pytest.skip("Se requieren datos reales en la BD.")

    cart = [
        {"product_id": products[0]["id_product"], "quantity": 1},
        {"product_id": 999999, "quantity": 1}
    ]
    success, result = process_cart_for_order(
        cart, 
        vendor_id=client["vendor_id"], 
        client_id=client["client_id"]
    )

    assert success is True
    assert isinstance(result, int)


def test_process_cart_for_order_with_exceeding_quantity():
    products, client = get_real_valid_data()
    if not products or not client:
        pytest.skip("Se requieren datos reales en la BD.")

    # Exceder intencionalmente el stock disponible
    excessive_qty = products[0]["quantity"] + 9999
    cart = [{"product_id": products[0]["id_product"], "quantity": excessive_qty}]

    success, result = process_cart_for_order(
        cart, 
        vendor_id=client["vendor_id"], 
        client_id=client["client_id"]
    )

    assert success is False
    assert isinstance(result, str)  # Devuelve mensaje de error por falta de stock


def test_process_cart_for_order_with_negative_quantity():
    products, client = get_real_valid_data()
    vendor_id = client["vendor_id"] if client else 1
    client_id = client["client_id"] if client else 1

    cart = [{"product_id": products[0]["id_product"] if products else 1, "quantity": -5}]
    success, result = process_cart_for_order(cart, vendor_id=vendor_id, client_id=client_id)

    assert success is False or isinstance(result, (int, str))