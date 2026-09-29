// Static mockup: fake data, every state from docs/design.md §States, exact copy.
const LAPTOPS = [
  { id: "aero-13", name: "Aero 13", price: 849, weight: 1.1, battery: 14, screen: 13.3, pitch: "Light enough to forget it's in your bag." },
  { id: "nimbus-14", name: "Nimbus 14", price: 899, weight: 1.3, battery: 16, screen: 14, pitch: "All-day battery in a slim aluminium shell." },
  { id: "studio-16", name: "Studio 16", price: 1799, weight: 2.1, battery: 10, screen: 16, pitch: "A big, colour-accurate screen for creative work." },
  { id: "forge-15", name: "Forge 15", price: 1399, weight: 2.4, battery: 6, screen: 15.6, pitch: "Gaming-grade graphics for play and 3D." },
  { id: "scholar-14", name: "Scholar 14", price: 499, weight: 1.5, battery: 11, screen: 14, pitch: "Everything a student needs, for less." },
  { id: "summit-13", name: "Summit 13 Pro", price: 1249, weight: 1.2, battery: 20, screen: 13.5, pitch: "The longest battery in the range." },
];
const Q_TRAVEL = "Which laptop is best for travel under £900?";
const Q_BATTERY = "Which one has the longest battery life?";
const Q_NONE = "Do you have a tablet under £200?";
const REPLY_TRAVEL = "For travel under £900, pick the Aero 13 (1.1 kg, £849) or the Nimbus 14 (1.3 kg, £899): both are light, and the Nimbus lasts two hours longer.";
const REPLY_NONE = "I can only recommend the six laptops on this page, and none of them is a tablet or costs under £200.";

const STATES = {
  "default":       { grid: "ready", chat: [] },
  "grid-loading":  { grid: "loading", chat: [] },
  "grid-error":    { grid: "error", chat: [] },
  "chat-thinking": { grid: "ready", chat: [["user", Q_TRAVEL], ["thinking"]], busy: true },
  "chat-reply":    { grid: "ready", chat: [["user", Q_TRAVEL], ["bot", REPLY_TRAVEL]], highlight: ["aero-13", "nimbus-14"] },
  "chat-no-match": { grid: "ready", chat: [["user", Q_NONE], ["bot", REPLY_NONE], ["caption", "No laptop on this page matches that."]] },
  "chat-error":    { grid: "ready", chat: [["user", Q_TRAVEL], ["error"]] },
};

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const gbp = (n) => "£" + n.toLocaleString("en-GB");

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
    retry.onclick = () => show("default");
    box.append(el("p", "error-text", "We couldn't load the laptops."), retry);
    grid.append(box);
    return;
  }
  for (const p of LAPTOPS) {
    const card = el("article", "card");
    if (highlight.includes(p.id)) { card.classList.add("recommended"); card.append(el("span", "badge", "Recommended")); }
    const ask = el("button", "pill", "Ask about this");
    ask.onclick = () => { const i = $("#chat-input"); i.value = `Tell me about the ${p.name}.`; i.focus(); };
    card.append(
      el("h3", null, p.name),
      el("div", "price", gbp(p.price)),
      el("p", "specs", `${p.weight} kg · ${p.battery} h battery · ${p.screen}″ screen`),
      el("p", "pitch", p.pitch),
      ask,
    );
    grid.append(card);
  }
}

function renderChat(items, busy) {
  const box = $("#messages");
  box.replaceChildren();
  if (!items.length) {
    box.append(el("p", "hint", "Not sure which one? Ask me. For example:"));
    for (const [q, state] of [[Q_TRAVEL, "chat-reply"], [Q_BATTERY, "chat-thinking"]]) {
      const chip = el("button", "chip", q);
      chip.onclick = () => show(state);
      box.append(chip);
    }
  }
  for (const [kind, text] of items) {
    if (kind === "user") box.append(el("p", "bubble user", text));
    if (kind === "bot") box.append(el("p", "bubble bot", text));
    if (kind === "thinking") box.append(el("p", "bubble bot", "Thinking…"));
    if (kind === "caption") box.append(el("p", "caption", text));
    if (kind === "error") {
      box.append(el("p", "bubble bot error", "Sorry, the assistant didn't answer. Try again."));
      const again = el("button", "pill secondary", "Try again");
      again.style.alignSelf = "flex-start";
      again.onclick = () => show("chat-thinking");
      box.append(again);
    }
  }
  $("#chat-input").disabled = !!busy;
  $("#chat-form button").disabled = !!busy;
}

function show(name) {
  const s = STATES[name];
  renderGrid(s.grid, s.highlight);
  renderChat(s.chat, s.busy);
  document.querySelectorAll(".statebar button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.state === name));
}

document.querySelectorAll(".statebar button").forEach((b) => (b.onclick = () => show(b.dataset.state)));
$("#chat-form").onsubmit = (e) => { e.preventDefault(); show("chat-thinking"); };
// Open a state directly with #state-name, e.g. index.html#chat-reply.
show(STATES[location.hash.slice(1)] ? location.hash.slice(1) : "default");
