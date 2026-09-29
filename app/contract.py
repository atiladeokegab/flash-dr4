"""The shared contract between the core, the providers and the web page."""
from typing import Literal

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    name: str
    price_gbp: float
    weight_kg: float
    battery_hours: float
    screen_in: float
    pitch: str


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    history: list[Message] = Field(default_factory=list, max_length=10)


class ChatReply(BaseModel):
    reply: str
    product_ids: list[str]
    provider: str


class ProviderError(Exception):
    """A provider failed; the core answers 502 {"error": "provider_failed"}."""
