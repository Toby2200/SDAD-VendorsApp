import pytest

from sales import catalog_client, service
from sales.catalog_client import CatalogUnavailable
from tests.data import ANDRES, CARREFOUR, MARIA, MERCADONA, WALMART

RESERVED = [{"product_id": 7, "code": "992831", "description": "Producto A",
             "unit_price": 10.99, "quantity": 2, "subtotal": 21.98}]
CART = [{"product_id": 7, "quantity": 2}]


@pytest.fixture
def fake_catalog(monkeypatch):
    """Reemplaza las llamadas HTTP a catalog y apunta qué se llamó."""
    calls = {"reserve": [], "release": [], "reserve_result": (True, RESERVED)}

    def reserve(items, token):
        calls["reserve"].append(items)
        result = calls["reserve_result"]
        if isinstance(result, Exception):
            raise result
        return result

    def release(items, token):
        calls["release"].append(items)

    monkeypatch.setattr(catalog_client, "reserve_stock", reserve)
    monkeypatch.setattr(catalog_client, "release_stock", release)
    return calls


def test_clients_are_filtered_by_vendor_and_search():
    assert sorted(c["name"] for c in service.get_clients_by_vendor(ANDRES)) == ["Carrefour", "Mercadona"]
    assert [c["name"] for c in service.get_clients_by_vendor(MARIA)] == ["Walmart"]
    assert [c["name"] for c in service.get_clients_by_vendor(ANDRES, "Carr")] == ["Carrefour"]


def test_clients_route(client, auth_headers):
    response = client.get("/sales/clients?search=Merc", headers=auth_headers)
    assert response.status_code == 200
    assert [c["client_id"] for c in response.get_json()] == [MERCADONA]


def test_order_is_saved_with_the_snapshot_from_catalog(fake_catalog, db_rows):
    success, order_id = service.process_cart_for_order(CART, ANDRES, CARREFOUR, "token")
    assert success
    details = db_rows("SELECT * FROM orderDetails WHERE id_order = %s", (order_id,))
    assert len(details) == 1
    assert details[0]["code"] == "992831"
    assert float(details[0]["unit_price"]) == 10.99


def test_empty_cart_is_rejected(fake_catalog):
    success, _ = service.process_cart_for_order([], ANDRES, MERCADONA, "token")
    assert not success
    assert fake_catalog["reserve"] == []


def test_client_of_another_vendor_is_rejected_before_calling_catalog(fake_catalog, db_rows):
    success, _ = service.process_cart_for_order(CART, ANDRES, WALMART, "token")
    assert not success
    assert fake_catalog["reserve"] == []
    assert db_rows("SELECT * FROM orders") == []


def test_no_stock_in_catalog_saves_nothing(fake_catalog, db_rows):
    fake_catalog["reserve_result"] = (False, "No hay stock suficiente")
    success, message = service.process_cart_for_order(CART, ANDRES, MERCADONA, "token")
    assert not success
    assert message == "No hay stock suficiente"
    assert db_rows("SELECT * FROM orders") == []


def test_stock_is_released_when_saving_the_order_fails(fake_catalog, db_rows):
    broken = [dict(RESERVED[0], code=None)]  # code es NOT NULL, el INSERT falla
    fake_catalog["reserve_result"] = (True, broken)
    with pytest.raises(Exception):
        service.process_cart_for_order(CART, ANDRES, MERCADONA, "token")
    assert fake_catalog["release"] == [CART]          # compensación
    assert db_rows("SELECT * FROM orders") == []      # rollback en sales


def test_order_route_status_codes(client, auth_headers, fake_catalog):
    ok = client.post("/sales/orders", json={"client_id": MERCADONA, "cart_items": CART}, headers=auth_headers)
    assert ok.status_code == 201
    assert isinstance(ok.get_json()["order_id"], int)

    bad = client.post("/sales/orders", json={"client_id": "1", "cart_items": CART}, headers=auth_headers)
    assert bad.status_code == 400
    empty = client.post("/sales/orders", json={"client_id": MERCADONA, "cart_items": []}, headers=auth_headers)
    assert empty.status_code == 400

    other = client.post("/sales/orders", json={"client_id": WALMART, "cart_items": CART}, headers=auth_headers)
    assert other.status_code == 409


def test_order_route_returns_503_when_catalog_is_unavailable(client, auth_headers, fake_catalog):
    fake_catalog["reserve_result"] = CatalogUnavailable("down")
    response = client.post("/sales/orders", json={"client_id": MERCADONA, "cart_items": CART}, headers=auth_headers)
    assert response.status_code == 503
    assert "error" in response.get_json()