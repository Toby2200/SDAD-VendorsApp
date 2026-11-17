import os

import requests

CATALOG_URL = os.getenv("CATALOG_URL", "http://127.0.0.1:8001")
CATALOG_TIMEOUT_S = float(os.getenv("CATALOG_TIMEOUT_S", "2"))

class CatalogUnavailable(Exception):
    """Catalog no respondió: está caído, tardó demasiado o devolvió un error inesperado."""

def _post(path, body, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        return requests.post(f"{CATALOG_URL}{path}", json=body, headers=headers, timeout=CATALOG_TIMEOUT_S)
    except (requests.ConnectionError, requests.Timeout) as error:
        raise CatalogUnavailable(f"No se pudo contactar con catalog: {error}") from error

def reserve_stock(items, token):
    response = _post("/products/reserve", {"selected_items": items}, token)

    if response.status_code == 200:
        return True, response.json()["items"]
    if response.status_code == 409:
        return False, response.json()["error"]

    raise CatalogUnavailable(f"Respuesta inesperada de catalog: {response.status_code}")

def release_stock(items, token):
    response = _post("/products/release", {"selected_items": items}, token)

    if response.status_code != 200:
        raise CatalogUnavailable(f"No se pudo liberar el stock: {response.status_code}")