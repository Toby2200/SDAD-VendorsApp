import pytest
import requests

from sales import catalog_client
from sales.catalog_client import CatalogUnavailable


class FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body


def fake_post(monkeypatch, response=None, error=None):
    sent = {}

    def post(url, json, headers, timeout):
        sent.update(url=url, json=json, headers=headers, timeout=timeout)
        if error:
            raise error
        return response

    monkeypatch.setattr(catalog_client.requests, "post", post)
    return sent


def test_reserve_sends_the_token_and_a_timeout(monkeypatch):
    sent = fake_post(monkeypatch, FakeResponse(200, {"items": ["x"]}))
    assert catalog_client.reserve_stock([{"product_id": 1, "quantity": 1}], "abc") == (True, ["x"])
    assert sent["url"].endswith("/products/reserve")
    assert sent["headers"]["Authorization"] == "Bearer abc"
    assert sent["timeout"] == catalog_client.CATALOG_TIMEOUT_S


def test_reserve_409_means_no_stock(monkeypatch):
    fake_post(monkeypatch, FakeResponse(409, {"error": "sin stock"}))
    assert catalog_client.reserve_stock([], "abc") == (False, "sin stock")


@pytest.mark.parametrize("error", [requests.ConnectionError("down"), requests.Timeout("slow")])
def test_network_errors_become_catalog_unavailable(monkeypatch, error):
    fake_post(monkeypatch, error=error)
    with pytest.raises(CatalogUnavailable):
        catalog_client.reserve_stock([], "abc")


def test_unexpected_status_codes_become_catalog_unavailable(monkeypatch):
    fake_post(monkeypatch, FakeResponse(500))
    with pytest.raises(CatalogUnavailable):
        catalog_client.reserve_stock([], "abc")
    with pytest.raises(CatalogUnavailable):
        catalog_client.release_stock([], "abc")


def test_release_ok(monkeypatch):
    sent = fake_post(monkeypatch, FakeResponse(200, {"message": "ok"}))
    catalog_client.release_stock([{"product_id": 1, "quantity": 1}], "abc")
    assert sent["url"].endswith("/products/release")