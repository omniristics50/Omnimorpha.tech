console.log("✅ dashboard.js loaded");

// ✅ MUST be your Render URL (not localhost)
const API_BASE = "https://omnimorpha-tech.onrender.com";

const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "—";
};

async function fetchJSON(path) {
  const url = `${API_BASE}${path}`;
  console.log("📡 Fetching:", url);

  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function tick() {
  try {
    const state = await fetchJSON("/v1/state");

    // Map to your backend schema
    setText("health", state?.health?.index != null ? `${state.health.index}%` : "—");
    setText("risk", state?.risk?.score != null ? `${state.risk.score}/100` : "—");
    setText("fleet", state?.fleet?.status ?? "SINGLE INSTANCE");

    const top = state?.strategies?.[0];
    setText("topStrategy", top?.title ?? "—");
    setText("reasoning", state?.explain?.narrative ?? "—");

    document.body.classList.add("nexus-live");
    document.body.classList.remove("nexus-offline");
  } catch (err) {
    console.warn("NEXUS offline:", err);
    document.body.classList.add("nexus-offline");
    document.body.classList.remove("nexus-live");

    setText("fleet", "OFFLINE / DEMO");
    setText("reasoning", `Backend not reachable. (${err?.message ?? "unknown error"})`);
  }
}

tick();
setInterval(tick, 2500);
