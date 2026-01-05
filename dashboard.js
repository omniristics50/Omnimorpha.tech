console.log("✅ dashboard.js loaded");

// Change this ONLY when your backend is deployed
const API_BASE = window.NEXUS_API_BASE || "http://127.0.0.1:8000";

const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "—";
};

async function fetchJSON(path) {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function tick() {
  try {
    const state = await fetchJSON("/v1/state");

    setText("health", state?.health?.index ? `${state.health.index}%` : "—");
    setText("risk", state?.risk?.score ? `${state.risk.score}/100` : "—");

    setText("fleet", state?.fleet?.status || "SINGLE INSTANCE");

    const top = state?.strategies?.[0];
    setText("topStrategy", top?.title || "—");

    setText("reasoning", state?.explain?.narrative || "—");

    document.body.classList.add("nexus-live");
    document.body.classList.remove("nexus-offline");

  } catch (err) {
    console.warn("NEXUS offline:", err.message);
    document.body.classList.add("nexus-offline");
    document.body.classList.remove("nexus-live");

    setText("fleet", "OFFLINE / DEMO");
    setText("reasoning", "Backend not reachable.");
  }
}

tick();
setInterval(tick, 2500);
