"""Shop Assistant core: the catalog, the chat endpoint and the web page."""
import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.contract import ChatReply, ChatRequest, Product, ProviderError

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "products.json"
WEB = ROOT / "web"

try:
    from app.assistant import get_provider
except ModuleNotFoundError as e:
    if e.name != "app.assistant":
        raise

    # Inline stub until app.assistant lands (#3).
    class _InlineStub:
        name = "stub"

        def reply(self, message, history, catalog):
            return "Here are two good options.", [p["id"] for p in catalog[:2]]

    def get_provider():
        return _InlineStub()


def load_catalog() -> list[dict]:
    if not CATALOG.exists():
        return []
    return json.loads(CATALOG.read_text(encoding="utf-8"))


app = FastAPI(title="Shop Assistant")


@app.get("/products", response_model=list[Product])
def products():
    return load_catalog()


@app.post("/chat", response_model=ChatReply)
def chat(req: ChatRequest):
    catalog = load_catalog()
    provider = get_provider()
    history = [m.model_dump() for m in req.history]
    try:
        reply, ids = provider.reply(req.message, history, catalog)
    except ProviderError:
        return JSONResponse(status_code=502, content={"error": "provider_failed"})
    known = {p["id"] for p in catalog}
    return ChatReply(reply=reply, product_ids=[i for i in ids if i in known], provider=provider.name)


if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
