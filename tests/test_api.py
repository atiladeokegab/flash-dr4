import json

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.contract import ProviderError

LAPTOPS = [
    {"id": f"lap-{i}", "name": f"Laptop {i}", "price_gbp": 500 + i * 100, "weight_kg": 1.2,
     "battery_hours": 10, "screen_in": 14, "pitch": "A laptop."}
    for i in range(3)
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    catalog = tmp_path / "products.json"
    catalog.write_text(json.dumps(LAPTOPS))
    monkeypatch.setattr(main, "CATALOG", catalog)
    monkeypatch.setenv("ASSISTANT_PROVIDER", "stub")
    return TestClient(main.app)


class FakeProvider:
    name = "fake"

    def __init__(self, ids=(), error=False):
        self.ids, self.error = list(ids), error

    def reply(self, message, history, catalog):
        if self.error:
            raise ProviderError("boom")
        return "ok", self.ids


def test_products(client):
    r = client.get("/products")
    assert r.status_code == 200
    assert r.json() == LAPTOPS


def test_products_empty_when_catalog_missing(client, monkeypatch, tmp_path):
    monkeypatch.setattr(main, "CATALOG", tmp_path / "missing.json")
    assert client.get("/products").json() == []


def test_chat_with_stub(client):
    r = client.post("/chat", json={"message": "which is best for travel?"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"] and body["provider"] == "stub"
    assert set(body["product_ids"]) <= {p["id"] for p in LAPTOPS}


@pytest.mark.parametrize("payload", [
    {"message": ""},
    {"message": "x" * 501},
    {"message": "hi", "history": [{"role": "user", "content": "hi"}] * 11},
])
def test_chat_rejects_bad_input(client, payload):
    assert client.post("/chat", json=payload).status_code == 422


def test_chat_accepts_limits(client, monkeypatch):
    monkeypatch.setattr(main, "get_provider", lambda: FakeProvider())
    payload = {"message": "x" * 500, "history": [{"role": "assistant", "content": "hi"}] * 10}
    assert client.post("/chat", json=payload).status_code == 200


def test_chat_provider_error_is_502(client, monkeypatch):
    monkeypatch.setattr(main, "get_provider", lambda: FakeProvider(error=True))
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 502
    assert r.json() == {"error": "provider_failed"}


def test_chat_drops_unknown_ids(client, monkeypatch):
    monkeypatch.setattr(main, "get_provider", lambda: FakeProvider(ids=["lap-1", "nope", "lap-2"]))
    r = client.post("/chat", json={"message": "hi"})
    assert r.json() == {"reply": "ok", "product_ids": ["lap-1", "lap-2"], "provider": "fake"}
