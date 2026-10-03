from sales.service import get_clients_by_vendor

#test for get_clients_by_vendor function
def test_get_clients_by_vendor_id1():
    clients = get_clients_by_vendor(1)

    assert len(clients) == 4
    assert clients[0]["name"] == "Mercadona"
    assert clients[1]["name"] == "Carrefour"

def test_get_clients_by_vendor_id2():
    clients = get_clients_by_vendor(2)

    assert len(clients) == 2
    assert clients[0]["name"] == "Walmart"

def test_get_clients_by_vendor_with_invalid_id():
    clients = get_clients_by_vendor(999)

    assert len(clients) == 0