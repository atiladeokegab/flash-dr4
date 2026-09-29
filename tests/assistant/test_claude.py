from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from app.assistant import ClaudeProvider, get_provider
from app.contract import ProviderError
from tests.assistant.test_stub import CATALOG


def provider_returning(text):
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(content=[SimpleNamespace(text=text)])
    return ClaudeProvider(client=client), client


def test_good_json_returns_reply_and_ids():
    provider, client = provider_returning('{"reply": "Try the Aero 13.", "product_ids": ["aero"]}')
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    assert provider.reply("light laptop?", history, CATALOG) == ("Try the Aero 13.", ["aero"])
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-haiku-4-5-20251001"
    assert '"aero"' in kwargs["system"]
    assert kwargs["messages"][-1] == {"role": "user", "content": "light laptop?"}
    assert len(kwargs["messages"]) == 3


def test_fenced_json_is_accepted():
    provider, _ = provider_returning('```json\n{"reply": "ok", "product_ids": []}\n```')
    assert provider.reply("hi", [], CATALOG) == ("ok", [])


@pytest.mark.parametrize("text", ["not json", '{"reply": "x"}', '{"reply": 1, "product_ids": "aero"}'])
def test_bad_json_raises_provider_error(text):
    provider, _ = provider_returning(text)
    with pytest.raises(ProviderError):
        provider.reply("hi", [], CATALOG)


def test_api_error_raises_provider_error():
    client = MagicMock()
    client.messages.create.side_effect = anthropic.APIConnectionError(
        request=httpx.Request("POST", "https://api.anthropic.com")
    )
    with pytest.raises(ProviderError):
        ClaudeProvider(client=client).reply("hi", [], CATALOG)


def test_get_provider_picks_claude(monkeypatch):
    monkeypatch.setenv("ASSISTANT_PROVIDER", "claude")
    monkeypatch.setattr(anthropic, "Anthropic", MagicMock())
    assert get_provider().name == "claude"
