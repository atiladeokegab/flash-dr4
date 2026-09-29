import json
from pathlib import Path

from app.assistant import StubProvider
from app.contract import Product

CATALOG = json.loads((Path(__file__).parent.parent / "data" / "products.json").read_text())
FIELDS = {"id": str, "name": str, "price_gbp": (int, float), "weight_kg": (int, float),
          "battery_hours": (int, float), "screen_in": (int, float), "pitch": str}


def test_six_unique_ids():
    assert len(CATALOG) == 6
    assert len({p["id"] for p in CATALOG}) == 6


def test_every_field_present_and_typed():
    for p in CATALOG:
        assert set(p) == set(FIELDS)
        for key, kind in FIELDS.items():
            assert isinstance(p[key], kind), (p["id"], key)
        Product(**p)


def ids(message):
    return StubProvider().reply(message, [], CATALOG)[1]


def test_stub_picks_differ_by_question():
    assert ids("Which laptop is best for travel under £900?") == ["aero-13", "nimbus-14"]
    assert ids("Which one has the longest battery life?") == ["summit-13"]
    assert ids("Anything under £900?") == ["scholar-14"]
    assert ids("Do you have a tablet under £200?") == []
