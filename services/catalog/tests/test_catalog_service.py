from catalog.service import get_available_products, validate

# ==========================================
# PRUEBAS PARA: get_available_products()
# ==========================================

def test_get_available_products_returns_only_active_and_in_stock():
    products = get_available_products()
    ids = sorted(product["id_product"] for product in products)

    assert ids == [1, 2, 5, 7, 8, 10]

def test_get_available_products_search_by_code():
    products = get_available_products(search_query="9928")
    
    assert len(products) == 1
    assert products[0]["code"] == "992831"


def test_get_available_products_search_by_description():
    products = get_available_products(search_query="A")
    
    assert len(products) == 2
    assert products[0]["description"] == "Producto A"


# ==========================================
# PRUEBAS PARA: validate()
# ==========================================

def test_validate_empty_items():
    cart, warnings = validate([])
    
    assert cart == []
    assert len(warnings) == 1
    assert "No se seleccionó ningún producto" in warnings[0]


def test_validate_valid_selection():
    items = [{"product_id": 1, "quantity": 2}]
    cart, warnings = validate(items)
    
    assert len(cart) == 1
    assert cart[0] == {"product_id": 1, "quantity": 2}
    assert len(warnings) == 0


def test_validate_adjusts_negative_or_zero_quantity():
    items = [{"product_id": 1, "quantity": -5}]
    cart, warnings = validate(items)
    
    assert cart[0]["quantity"] == 1


def test_validate_adjusts_quantity_exceeding_stock():
    items = [{"product_id": 1, "quantity": 50}]
    cart, warnings = validate(items)
    
    assert cart[0]["quantity"] == 10
    assert len(warnings) == 1
    assert "superaba el stock" in warnings[0]


def test_validate_ignores_inactive_or_out_of_stock_product():
    items = [{"product_id": 4, "quantity": 1}]
    cart, warnings = validate(items)
    
    assert cart == []
    assert len(warnings) == 1
    assert "ya no está disponible" in warnings[0]