from catalog.service import get_available_products, get_product_by_ids, release_stock, reserve_stock

PRODUCT_A = "992831"        # activo, stock 10, 10.99
PRODUCT_B = "23234432 C"    # activo, stock 0
PRODUCT_C = "4564645 D"     # inactivo, stock 20
PRODUCT_D = "5466456 E"     # activo, stock 15


def test_available_products_only_returns_active_products_with_stock():
    products = get_available_products()
    assert len(products) == 6
    assert all(p["active"] and p["quantity"] > 0 for p in products)


def test_prices_are_numbers_ready_for_json():
    product = get_available_products(PRODUCT_A)[0]
    assert product["price"] == 10.99
    assert isinstance(product["price"], float)


def test_search_by_code_and_by_description():
    assert [p["code"] for p in get_available_products("992")] == [PRODUCT_A]
    assert [p["code"] for p in get_available_products("Producto D")] == [PRODUCT_D]
    assert get_available_products("does-not-exist") == []


def test_product_details_skip_inactive_products(product_id):
    details = get_product_by_ids([product_id(PRODUCT_A), product_id(PRODUCT_C)])
    assert [d["code"] for d in details] == [PRODUCT_A]


def test_product_details_with_empty_list():
    assert get_product_by_ids([]) == []


def test_reserve_subtracts_stock_and_returns_the_snapshot(product_id, stock_of):
    success, items = reserve_stock([{"product_id": product_id(PRODUCT_A), "quantity": 3}])
    assert success
    assert items[0]["code"] == PRODUCT_A
    assert items[0]["unit_price"] == 10.99
    assert items[0]["subtotal"] == 32.97
    assert stock_of(PRODUCT_A) == 7


def test_reserve_more_than_stock_is_rejected_and_stock_is_unchanged(product_id, stock_of):
    success, message = reserve_stock([{"product_id": product_id(PRODUCT_A), "quantity": 999}])
    assert not success
    assert "stock" in message
    assert stock_of(PRODUCT_A) == 10


def test_reserve_is_all_or_nothing(product_id, stock_of):
    items = [
        {"product_id": product_id(PRODUCT_A), "quantity": 1},
        {"product_id": product_id(PRODUCT_B), "quantity": 1},  # sin stock
    ]
    success, _ = reserve_stock(items)
    assert not success
    assert stock_of(PRODUCT_A) == 10  # el primer producto tampoco se descontó


def test_reserve_rejects_inactive_products(product_id, stock_of):
    success, _ = reserve_stock([{"product_id": product_id(PRODUCT_C), "quantity": 1}])
    assert not success
    assert stock_of(PRODUCT_C) == 20


def test_reserve_rejects_zero_or_negative_quantities(product_id, stock_of):
    success, _ = reserve_stock([{"product_id": product_id(PRODUCT_A), "quantity": -5}])
    assert not success
    assert stock_of(PRODUCT_A) == 10


def test_reserve_unknown_product():
    success, _ = reserve_stock([{"product_id": 999999, "quantity": 1}])
    assert not success


def test_release_gives_stock_back(product_id, stock_of):
    success, _ = release_stock([{"product_id": product_id(PRODUCT_A), "quantity": 2}])
    assert success
    assert stock_of(PRODUCT_A) == 12


def test_release_unknown_product_or_bad_quantity(product_id, stock_of):
    assert release_stock([{"product_id": 999999, "quantity": 1}])[0] is False
    assert release_stock([{"product_id": product_id(PRODUCT_A), "quantity": 0}])[0] is False
    assert stock_of(PRODUCT_A) == 10