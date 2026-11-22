import threading
import time

import pytest
from flask import Flask, jsonify, request
from werkzeug.serving import make_server

from sales import catalog_client, service
from tests.data import ANDRES, MERCADONA


def build_stub_catalog(state):
    stub = Flask("stub_catalog")

    @stub.post("/products/reserve")
    def reserve():
        state["calls"].append(("reserve", request.headers.get("Authorization"), request.get_json()))
        if state["delay_s"]:
            time.sleep(state["delay_s"])
        items = request.get_json()["selected_items"]
        if any(item["quantity"] > state["stock"] for item in items):
            return jsonify({"error": "El producto no tiene stock suficiente."}), 409
        state["stock"] -= sum(item["quantity"] for item in items)
        code = state["code"]
        return jsonify({"items": [
            {"product_id": i["product_id"], "code": code, "description": "Producto A",
             "unit_price": 10.0, "quantity": i["quantity"], "subtotal": 10.0 * i["quantity"]}
            for i in items
        ]}), 200

    @stub.post("/products/release")
    def release():
        state["calls"].append(("release", request.headers.get("Authorization"), request.get_json()))
        state["stock"] += sum(item["quantity"] for item in request.get_json()["selected_items"])
        return jsonify({"message": "ok"}), 200

    return stub


@pytest.fixture
def stub_catalog(monkeypatch):
    state = {"calls": [], "stock": 5, "delay_s": 0, "code": "992831"}
    server = make_server("127.0.0.1", 0, build_stub_catalog(state), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(catalog_client, "CATALOG_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setattr(catalog_client, "CATALOG_TIMEOUT_S", 0.5)
    yield state
    server.shutdown()


def order(client, auth_headers, quantity):
    body = {"client_id": MERCADONA, "cart_items": [{"product_id": 1, "quantity": quantity}]}
    return client.post("/sales/orders", json=body, headers=auth_headers)


def test_order_crosses_the_seam_and_forwards_the_token(client, auth_headers, token, stub_catalog, db_rows):
    response = order(client, auth_headers, 2)
    assert response.status_code == 201
    assert stub_catalog["stock"] == 3
    assert stub_catalog["calls"][0][1] == f"Bearer {token}"
    order_id = response.get_json()["order_id"]
    assert db_rows("SELECT code FROM orderDetails WHERE id_order = %s", (order_id,))[0]["code"] == "992831"


def test_no_stock_answer_from_catalog_becomes_409(client, auth_headers, stub_catalog, db_rows):
    response = order(client, auth_headers, 99)
    assert response.status_code == 409
    assert "stock" in response.get_json()["error"]
    assert db_rows("SELECT * FROM orders") == []


def test_slow_catalog_times_out_with_503(client, auth_headers, stub_catalog):
    stub_catalog["delay_s"] = 2  # más que el timeout de 0.5 s
    started = time.monotonic()
    response = order(client, auth_headers, 1)
    assert response.status_code == 503
    assert time.monotonic() - started < 2


def test_catalog_down_returns_503(client, auth_headers, monkeypatch):
    monkeypatch.setattr(catalog_client, "CATALOG_URL", "http://127.0.0.1:9")  # nadie escucha
    response = order(client, auth_headers, 1)
    assert response.status_code == 503
    assert "error" in response.get_json()


def test_failed_save_releases_the_stock_in_catalog(stub_catalog, token, db_rows):
    stub_catalog["code"] = None  # orderDetails.code es NOT NULL, el INSERT falla
    with pytest.raises(Exception):
        service.process_cart_for_order([{"product_id": 1, "quantity": 2}], ANDRES, MERCADONA, token)
    assert [call[0] for call in stub_catalog["calls"]] == ["reserve", "release"]
    assert stub_catalog["stock"] == 5
    assert db_rows("SELECT * FROM orders") == []