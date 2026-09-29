# /// script
# requires-python = ">=3.11"
# dependencies = ["diagrams"]
# ///
"""C4 diagrams for Shop Assistant, levels 1-4, drawn from the merged code."""

import shutil
import sys
from functools import partial
from pathlib import Path

from diagrams import Diagram
from diagrams.c4 import Container, Person, Relationship, System, SystemBoundary

Container, Person, System = (partial(f, width="3.3") for f in (Container, Person, System))

SYSTEM = "Shop Assistant"
OUT = Path(__file__).parent
GRAPH = {"splines": "spline", "nodesep": "0.8", "ranksep": "1.1"}


def draw(level, title):
    return Diagram(f"{SYSTEM} - {title}", filename=str(OUT / f"c4_{level}"), outformat="png",
                   show=False, direction="TB", graph_attr=GRAPH)


def context():
    with draw("context", "System Context"):
        user = Person("Shopper", "Wants one clear laptop recommendation")
        system = System(SYSTEM, "Laptop product page with an AI chat that recommends from the catalog")
        claude = System("Anthropic API", "Claude Haiku 4.5 answers from the catalog", external=True)
        user >> Relationship("browses, asks questions") >> system
        system >> Relationship("HTTPS, only when ASSISTANT_PROVIDER=claude") >> claude


def container():
    with draw("container", "Containers"):
        user = Person("Shopper", "")
        claude = System("Anthropic API", "LLM", external=True)
        with SystemBoundary(SYSTEM):
            page = Container("Web page", "HTML/CSS/JS in web/", "Product grid + chat widget (app.js)")
            api = Container("API server", "FastAPI app.main, uv", "GET /products, POST /chat; mounts web/ at /")
            catalog = Container("Catalog", "data/products.json", "Laptops, read on every request")
        user >> Relationship("browser") >> page
        page >> Relationship("fetch GET /products, POST /chat -> {reply, product_ids, provider}") >> api
        api >> Relationship("load_catalog()") >> catalog
        api >> Relationship("messages.create") >> claude


def component():
    with draw("component", "Components of the API server"):
        catalog = Container("data/products.json", "catalog", "Laptops")
        with SystemBoundary("API server"):
            main = Container("app.main", "FastAPI", "/products, /chat, static web/; drops unknown ids; 502 on ProviderError")
            contract = Container("app.contract", "pydantic", "Product, Message, ChatRequest, ChatReply, ProviderError")
            assistant = Container("app.assistant", "providers", "get_provider() by ASSISTANT_PROVIDER: stub (default) | claude")
        main >> Relationship("validates with") >> contract
        main >> Relationship("load_catalog()") >> catalog
        main >> Relationship("get_provider().reply(message, history, catalog)") >> assistant
        assistant >> Relationship("raises ProviderError") >> contract


def code():
    with draw("code", "Code"):
        claude_api = System("Anthropic API", "claude-haiku-4-5-20251001", external=True)
        with SystemBoundary("app.main"):
            chat = Container("chat(req)", "POST /chat", "catalog -> provider.reply -> filter known ids -> ChatReply")
            products = Container("products()", "GET /products", "returns load_catalog()")
            load = Container("load_catalog()", "function", "data/products.json, [] if missing")
        with SystemBoundary("app.contract"):
            req = Container("ChatRequest", "BaseModel", "message 1-500 chars, history <= 10 Message")
            reply = Container("ChatReply", "BaseModel", "reply, product_ids, provider")
            err = Container("ProviderError", "Exception", "-> 502 {error: provider_failed}")
        with SystemBoundary("app.assistant"):
            get = Container("get_provider()", "function", "ASSISTANT_PROVIDER: stub | claude, else ValueError")
            stub = Container("StubProvider", "class", "reply(): keyword rules (under £N, travel, battery, budget)")
            claude = Container("ClaudeProvider", "class", "reply(): catalog in system prompt, parses JSON")
        chat >> Relationship("takes") >> req
        chat >> Relationship("returns") >> reply
        chat >> Relationship("calls") >> load
        products >> Relationship("calls") >> load
        chat >> Relationship("calls") >> get
        get >> Relationship("returns") >> stub
        get >> Relationship("returns") >> claude
        claude >> Relationship("raises") >> err
        claude >> Relationship("messages.create") >> claude_api


LEVELS = {n: globals()[n] for n in ("context", "container", "component", "code") if n in globals()}

if __name__ == "__main__":
    if not shutil.which("dot"):
        sys.exit("c4: Graphviz is not installed (no `dot` on PATH). Run: sudo apt install -y graphviz")
    for name in sys.argv[1:] or LEVELS:
        LEVELS[name]()
        print(OUT / f"c4_{name}.png")
