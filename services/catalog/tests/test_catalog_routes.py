PRODUCT_A = "992831"


def test_routes_require_a_token(client):
    assert client.get("/products").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/products", headers=bad).status_code == 401


def test_list_and_search_products(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 6

    response = client.get("/products?search=992", headers=auth_headers)
    assert [p["code"] for p in response.get_json()] == [PRODUCT_A]


def test_details(client, auth_headers, product_id):
    response = client.post("/products/details", json={"product_ids": [product_id(PRODUCT_A)]}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()[0]["price"] == 10.99


def test_details_rejects_bad_bodies(client, auth_headers):
    assert client.post("/products/details", json={"product_ids": "1"}, headers=auth_headers).status_code == 400
    assert client.post("/products/details", json={"product_ids": ["x"]}, headers=auth_headers).status_code == 400


def test_reserve_ok(client, auth_headers, product_id, stock_of):
    body = {"selected_items": [{"product_id": product_id(PRODUCT_A), "quantity": 2}]}
    response = client.post("/products/reserve", json=body, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["items"][0]["quantity"] == 2
    assert stock_of(PRODUCT_A) == 8


def test_reserve_without_stock_returns_409(client, auth_headers, product_id):
    body = {"selected_items": [{"product_id": product_id(PRODUCT_A), "quantity": 999}]}
    response = client.post("/products/reserve", json=body, headers=auth_headers)
    assert response.status_code == 409
    assert "error" in response.get_json()


def test_reserve_rejects_malformed_bodies_with_400(client, auth_headers):
    bad_bodies = [
        {"selected_items": "not a list"},
        {"selected_items": [{"product_id": 1}]},
        {"selected_items": [{"product_id": "1", "quantity": 1}]},
    ]
    for body in bad_bodies:
        assert client.post("/products/reserve", json=body, headers=auth_headers).status_code == 400


def test_release(client, auth_headers, product_id, stock_of):
    body = {"selected_items": [{"product_id": product_id(PRODUCT_A), "quantity": 1}]}
    assert client.post("/products/release", json=body, headers=auth_headers).status_code == 200
    assert stock_of(PRODUCT_A) == 11

    body = {"selected_items": [{"product_id": 999999, "quantity": 1}]}
    assert client.post("/products/release", json=body, headers=auth_headers).status_code == 400

    body = {"selected_items": "not a list"}
    assert client.post("/products/release", json=body, headers=auth_headers).status_code == 400


def test_health_reports_the_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["db"] == "ok"


def test_cors_only_for_the_ui_origin(client):
    allowed = client.get("/health", headers={"Origin": "http://localhost:8080"})
    assert allowed.headers["Access-Control-Allow-Origin"] == "http://localhost:8080"

    other = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "Access-Control-Allow-Origin" not in other.headers