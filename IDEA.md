# The idea

The lead writes this once the team has agreed the idea, and no issue is created before it is
complete. If your task doesn't fit this page, open a change-request (AGENTS.md §7).

Grew from: Zeus's pitch (a solo dry run), in the Conversational Commerce track.

## Problem

Choosing between six laptops means reading six spec sheets. Shoppers want to ask a question in
plain words ("which is best for travel under £900?") and get one clear answer with a reason.

## The idea

**Shop Assistant** is a product page with a chat widget. Ask about the laptops on the page and an AI
assistant answers from the page's own catalog, recommends specific products, and says why. It never
recommends anything that isn't in the catalog.

## What we build

- `GET /products`: the catalog (6 laptops: id, name, price in GBP, weight, battery hours, screen, one-line pitch)
- `POST /chat` with `{"message": "...", "history": [...]}` returns `{"reply": "...", "product_ids": [...], "provider": "stub" | "claude"}`
- Providers chosen by `ASSISTANT_PROVIDER`: `stub` (default, offline: keyword rules) or `claude` (Claude Haiku 4.5, `ANTHROPIC_API_KEY` in `.env`)
- A product page in `web/`: the product grid and a chat widget; recommended products are highlighted in the grid

## What we don't build

- A cart, checkout, accounts or payments
- Products outside the catalog, or live prices
- Deployment: the demo runs on localhost from `main`

## The demo, in one line

Ask "which laptop is best for travel under £900?" and the assistant answers in a sentence and the right laptops light up on the page.

## Areas and owners

Each person owns their area's directories outright (AGENTS.md §6). The core is the shared
contracts; only the lead changes it.

| Area | Directories | Owner | Issues |
|---|---|---|---|
| core | `pyproject.toml`, `uv.lock`, `app/__init__.py`, `app/main.py`, `app/contract.py`, `tests/__init__.py`, `tests/test_api.py` | — | — |
| assistant | `app/assistant/`, `tests/assistant/` | — | — |
| catalog | `data/`, `tests/test_catalog.py` | — | — |
| web | `web/` | — | — |
| design | `docs/design.md`, `docs/mockup/` | @atiladeokegab [Zeus] | #1 |
| submission | `docs/pitch.md`, `docs/demo.md`, `docs/architecture/` | — | — |
