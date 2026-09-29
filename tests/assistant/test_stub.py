from app.assistant import StubProvider, get_provider

CATALOG = [
    {"id": "aero", "name": "Aero 13", "price_gbp": 1200, "weight_kg": 1.0, "battery_hours": 12, "screen_in": 13.3, "pitch": ""},
    {"id": "feather", "name": "Feather 14", "price_gbp": 850, "weight_kg": 1.1, "battery_hours": 10, "screen_in": 14, "pitch": ""},
    {"id": "trek", "name": "Trek 14", "price_gbp": 700, "weight_kg": 1.3, "battery_hours": 9, "screen_in": 14, "pitch": ""},
    {"id": "marathon", "name": "Marathon 15", "price_gbp": 950, "weight_kg": 1.8, "battery_hours": 20, "screen_in": 15.6, "pitch": ""},
    {"id": "saver", "name": "Saver 15", "price_gbp": 400, "weight_kg": 2.0, "battery_hours": 7, "screen_in": 15.6, "pitch": ""},
    {"id": "titan", "name": "Titan 17", "price_gbp": 2000, "weight_kg": 2.8, "battery_hours": 5, "screen_in": 17.3, "pitch": ""},
]


def ask(message):
    return StubProvider().reply(message, [], CATALOG)


def test_get_provider_defaults_to_stub(monkeypatch):
    monkeypatch.delenv("ASSISTANT_PROVIDER", raising=False)
    assert get_provider().name == "stub"


def test_travel_under_budget_picks_lightest_two_in_budget():
    reply, ids = ask("Which laptop is best for travel under £900?")
    assert ids == ["feather", "trek"]
    assert "Feather 14" in reply


def test_battery_picks_longest_battery():
    assert ask("I need great battery life")[1] == ["marathon"]


def test_cheap_picks_cheapest():
    assert ask("something cheap please")[1] == ["saver"]


def test_nothing_under_limit_returns_no_ids():
    reply, ids = ask("anything under £100?")
    assert ids == [] and "£100" in reply


def test_default_picks_first_two():
    assert ask("hello")[1] == ["aero", "feather"]
