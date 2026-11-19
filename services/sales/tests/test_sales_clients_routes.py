def test_select_clients_page_loads_when_logged_in(logged_in_client):
    response = logged_in_client.get("/sales/select-clients")

    assert response.status_code == 200


def test_select_clients_shows_only_clients_of_the_vendor(logged_in_client):
    response = logged_in_client.get("/sales/select-clients")
    html = response.get_data(as_text=True)

    assert "Mercadona" in html
    assert "Carrefour" in html
    assert "Walmart" not in html  # es cliente de Maria, no de Andres


def test_select_clients_other_vendor_sees_their_own_clients(client):
    with client.session_transaction() as session:
        session["vendor_id"] = 2 

    html = client.get("/sales/select-clients").get_data(as_text=True)

    assert "Walmart" in html
    assert "Mercadona" not in html


def test_select_clients_search_filters_by_name(logged_in_client):
    html = logged_in_client.get(
        "/sales/select-clients?search=Merc"
    ).get_data(as_text=True)

    assert "Mercadona" in html
    assert "Carrefour" not in html


def test_select_clients_search_cannot_find_other_vendors_clients(logged_in_client):
    html = logged_in_client.get(
        "/sales/select-clients?search=Walmart"
    ).get_data(as_text=True)

    assert "Walmart - Avenida Central" not in html


def test_select_client_saves_it_in_session_and_redirects_to_catalog(logged_in_client):
    response = logged_in_client.post(
        "/sales/select-clients",
        data={"client_id": "1"},
    )

    assert response.status_code == 302
    assert response.location == "/products"

    with logged_in_client.session_transaction() as session:
        assert session["selected_client_id"] == "1"