# Demo: Shop Assistant in 60 seconds

Run the demo from `main`: it is the last commit that passed the smoke check. Everything
below is typed from the repo root.

## Before you present (5 minutes, once)

1. Get the code and install:
   ```bash
   git checkout main && git pull
   uv sync
   ```
2. Put the Claude key in `.env` at the repo root (never commit it; `.env` is gitignored).
   The key is shared outside GitHub:
   ```bash
   echo "ANTHROPIC_API_KEY=<the key>" > .env
   ```
3. Start the app with Claude as the assistant:
   ```bash
   ASSISTANT_PROVIDER=claude uv run uvicorn app.main:app --port 8000
   ```
   PowerShell: `$env:ASSISTANT_PROVIDER="claude"; uv run uvicorn app.main:app --port 8000`
4. Open <http://localhost:8000> in a browser. Check before you start:
   - The grid shows the 6 laptops. If it shows "We couldn't load the laptops.", the server
     isn't running: go back to step 3.
   - Ask the demo question once as a rehearsal (below) and look at which cards light up.
     Note their names so you can say them aloud.
5. Open a second terminal at the repo root for the error beat. Then reload the page so the chat
   starts empty.

## The run-through (60 seconds)

| Time | Do | Say |
|---|---|---|
| 0–10 s | Show the page: headline, the grid of 6 laptop cards, the chat panel on the right. | "Six laptops, six spec sheets. Nobody wants to read them. So we added an assistant that knows this page." |
| 10–25 s | In the chat, tap the example "Which laptop is best for travel under £900?" (press **Send** if it only fills the box). "Thinking…" appears, then the reply. | "I ask in plain words, the way I'd ask a shop assistant." |
| 25–35 s | Point at the grid: the recommended laptops have an indigo ring and a "Recommended" badge. | "It answers in one sentence and the right laptops light up. It only ever recommends what's in this catalog." |
| 35–45 s | Ask a follow-up: "Which one has the longest battery life?" The highlights move to the new pick. | "It keeps the conversation, and the highlights follow the answer." |
| 45–55 s | Error beat: in the second terminal, send an empty message: `curl -s -X POST localhost:8000/chat -H "content-type: application/json" -d '{"message": ""}'` It answers 422. | "Bad input is refused at the door. If Claude fails, the page says 'Sorry, the assistant didn't answer. Try again.' instead of making something up." |
| 55–60 s | Back to the page. | "Shop Assistant: ask a question, get one clear answer from the page's own catalog." |

## If something goes wrong

- **No network, or Claude is down:** stop the server (Ctrl+C) and restart it with the offline
  stub. It answers from keyword rules and needs no key; the page looks exactly the same:
  ```bash
  ASSISTANT_PROVIDER=stub uv run uvicorn app.main:app --port 8000
  ```
  The stub also recommends the lightest laptops under £900 for the travel question, so the
  run-through doesn't change. The API reply says `"provider": "stub"`.
- **The chat shows "Sorry, the assistant didn't answer. Try again."** during the demo: the key is
  missing or wrong (the server answers 502 `{"error": "provider_failed"}`). Press "Try again" once;
  if it repeats, switch to the stub as above.
- **Port 8000 is taken:** use `--port 8001` and open <http://localhost:8001>.
- **The grid is empty:** `data/products.json` is missing; you're not on `main`.

## What's under the hood (if a judge asks)

- `GET /products` returns the 6 laptops from `data/products.json`.
- `POST /chat` takes `{"message": "...", "history": [...]}` (message 1–500 characters, up to 10
  history turns) and returns `{"reply": "...", "product_ids": [...], "provider": "claude" | "stub"}`.
  The server drops any product id that isn't in the catalog, so the assistant can't recommend
  something the shop doesn't sell.
- The assistant is Claude Haiku 4.5, chosen with `ASSISTANT_PROVIDER=claude`; `stub` is the
  offline default.
