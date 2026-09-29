"""Assistant providers behind get_provider(), chosen by ASSISTANT_PROVIDER."""

import os
import re


def _field(product, key):
    # Core may pass dicts or pydantic Products.
    return product[key] if isinstance(product, dict) else getattr(product, key)


class StubProvider:
    """Offline keyword rules from the spec; no network, no key."""

    name = "stub"

    def reply(self, message, history, catalog):
        text = message.lower()
        pool = list(catalog)
        under = re.search(r"under\s*£?\s*(\d+)", text)
        if under:
            limit = int(under.group(1))
            pool = [p for p in pool if _field(p, "price_gbp") <= limit]
            if not pool:
                return f"Nothing in the catalog is under £{limit}.", []

        if "travel" in text or "light" in text:
            picks = sorted(pool, key=lambda p: _field(p, "weight_kg"))[:2]
            why = "they are the lightest"
        elif "battery" in text:
            picks = sorted(pool, key=lambda p: -_field(p, "battery_hours"))[:1]
            why = "it has the longest battery life"
        elif under or "cheap" in text or "budget" in text:
            picks = sorted(pool, key=lambda p: _field(p, "price_gbp"))[:1]
            why = "it is the cheapest"
        else:
            picks = pool[:2]
            why = "they are our best all-rounders"

        names = " and ".join(_field(p, "name") for p in picks)
        return f"I'd pick {names}: {why}.", [_field(p, "id") for p in picks]


def get_provider():
    name = os.environ.get("ASSISTANT_PROVIDER", "stub")
    if name == "stub":
        return StubProvider()
    raise ValueError(f"Unknown ASSISTANT_PROVIDER: {name}")
