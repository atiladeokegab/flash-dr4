// Shop Assistant page: the grid loads from GET /products (docs/design.md §Screens, §States).
const Q_TRAVEL = "Which laptop is best for travel under £900?";
const Q_BATTERY = "Which one has the longest battery life?";

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const gbp = (n) => "£" + n.toLocaleString("en-GB");

let products = [];

function renderGrid(mode, highlight = []) {
  const grid = $("#grid");
  grid.replaceChildren();
  if (mode === "loading") {
    grid.append(el("p", "status", "Loading laptops…"));
    for (let i = 0; i < 6; i++) grid.append(el("div", "skeleton"));
    return;
  }
  if (mode === "error") {
    const box = el("div", "error-box");
    const retry = el("button", "pill", "Retry");
    retry.onclick = loadProducts;
    box.append(el("p", "error-text", "We couldn't load the laptops."), retry);
    grid.append(box);
    return;
  }
  for (const p of products) {
    const card = el("article", "card");
    card.dataset.id = p.id;
    if (highlight.includes(p.id)) { card.classList.add("recommended"); card.append(el("span", "badge", "Recommended")); }
    const ask = el("button", "pill", "Ask about this");
    ask.onclick = () => { const i = $("#chat-input"); i.value = `Tell me about the ${p.name}.`; i.focus(); };
    card.append(
      el("h3", null, p.name),
      el("div", "price", gbp(p.price_gbp)),
      el("p", "specs", `${p.weight_kg} kg · ${p.battery_hours} h battery · ${p.screen_in}″ screen`),
      el("p", "pitch", p.pitch),
      ask,
    );
    grid.append(card);
  }
}

async function loadProducts() {
  renderGrid("loading");
  try {
    const res = await fetch("/products");
    if (!res.ok) throw new Error(res.status);
    products = await res.json();
    renderGrid("ready");
  } catch {
    renderGrid("error");
  }
}

// Empty chat state; sending to /chat is #13.
function renderChatEmpty() {
  const box = $("#messages");
  box.replaceChildren(el("p", "hint", "Not sure which one? Ask me. For example:"));
  for (const q of [Q_TRAVEL, Q_BATTERY]) {
    const chip = el("button", "chip", q);
    chip.onclick = () => { $("#chat-input").value = q; };
    box.append(chip);
  }
}

$("#chat-form").onsubmit = (e) => e.preventDefault();
renderChatEmpty();
loadProducts();
