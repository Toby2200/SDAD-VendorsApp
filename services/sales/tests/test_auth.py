from auth.service import authenticate_vendor


def test_authenticate_with_correct_password():
    vendor = authenticate_vendor("andres@test.com", "123456")
    assert vendor["name"] == "Andres"


def test_authenticate_rejects_wrong_password_unknown_mail_and_inactive_vendor():
    assert authenticate_vendor("andres@test.com", "wrong") is None
    assert authenticate_vendor("nobody@test.com", "123456") is None
    assert authenticate_vendor("carlos@test.com", "password123") is None  # inactivo


def test_login_returns_a_token(client):
    response = client.post("/login", json={"mail": "andres@test.com", "password": "123456"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["token"]
    assert body["vendor"]["name"] == "Andres"


def test_login_errors(client):
    assert client.post("/login", json={"mail": "andres@test.com"}).status_code == 400
    assert client.post("/login", json={"mail": "andres@test.com", "password": "wrong"}).status_code == 401


def test_protected_routes_need_a_valid_token(client):
    assert client.get("/sales/clients").status_code == 401
    bad = {"Authorization": "Bearer forged.token.value"}
    assert client.get("/sales/clients", headers=bad).status_code == 401


def test_health_reports_the_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["db"] == "ok"