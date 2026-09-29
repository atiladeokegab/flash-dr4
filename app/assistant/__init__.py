"""Assistant providers behind get_provider(), chosen by ASSISTANT_PROVIDER."""

import json
import os
import re

import anthropic

from app.contract import ProviderError


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


class ClaudeProvider:
    """Claude Haiku 4.5 answering from the catalog as JSON {reply, product_ids}."""

    name = "claude"
    model = "claude-haiku-4-5-20251001"

    def __init__(self, client=None):
        self.client = client or anthropic.Anthropic()

    def reply(self, message, history, catalog):
        products = [p if isinstance(p, dict) else p.model_dump() for p in catalog]
        system = (
            "You are a shop assistant for the laptops below. Recommend only from this catalog.\n"
            f"Catalog: {json.dumps(products)}\n"
            'Answer with only a JSON object: {"reply": "<short answer>", '
            '"product_ids": ["<ids of the products you recommend>"]}'
        )
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": message})
        try:
            resp = self.client.messages.create(
                model=self.model, max_tokens=512, system=system, messages=messages
            )
            text = resp.content[0].text.strip()
            # Haiku sometimes wraps JSON in a ```json fence.
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
            data = json.loads(text)
            reply, ids = data["reply"], data["product_ids"]
        except (anthropic.APIError, ValueError, KeyError, IndexError, AttributeError, TypeError) as e:
            raise ProviderError(str(e)) from e
        if not isinstance(reply, str) or not isinstance(ids, list):
            raise ProviderError("bad reply shape")
        return reply, [str(i) for i in ids]


def get_provider():
    name = os.environ.get("ASSISTANT_PROVIDER", "stub")
    if name == "stub":
        return StubProvider()
    if name == "claude":
        return ClaudeProvider()
    raise ValueError(f"Unknown ASSISTANT_PROVIDER: {name}")
