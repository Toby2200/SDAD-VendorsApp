from app import app

def test_login_page_is_available():
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200

def test_login_with_correct_credentials_creates_session():
    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "mail": "andres@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 302
    assert response.location == "/sales/select-clients"

    with client.session_transaction() as session:
        assert session["vendor_id"] == 1

def test_login_with_wrong_password_is_rejected():
    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "mail": "andres@test.com",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401

def test_logout_clears_session():
    client = app.test_client()

    with client.session_transaction() as session:
        session["vendor_id"] = 1

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.location == "/login"

    with client.session_transaction() as session:
        assert "vendor_id" not in session