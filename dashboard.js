console.log("✅ dashboard.js loaded");

// =====================================================
// CONFIG
// =====================================================
const API_BASE = "https://omnimorpha-tech.onrender.com";
const POLL_INTERVAL_MS = 2500;

// =====================================================
// DOM HELPERS
// =====================================================
const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "—";
};

const setConn = (text) => {
  const el = document.getElementById("connectionText");
  if (el) el.textContent = text;
};

// =====================================================
// NETWORK
// =====================================================
async function fetchJSON(path) {
  const url = `${API_BASE}${path}`;
  console.log("📡 Fetching:", url);

  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// =====================================================
// MAIN LOOP
// =====================================================
async function tick() {
  try {
    const state = await fetchJSON("/v1/state");

    // -------------------------------
    // CORE KPIs
    // -------------------------------
    setText("health", state?.health?.index != null ? `${state.health.index}%` : "—");
    setText("risk", state?.risk?.score != null ? `${state.risk.score}/100` : "—");
    setText("fleet", state?.fleet?.status ?? "SINGLE INSTANCE");

    // -------------------------------
    // STRATEGY + REASONING
    // -------------------------------
    const topStrategy = state?.strategies?.[0];
    setText("topStrategy", topStrategy?.title ?? "—");
    setText("reasoning", state?.explain?.narrative ?? "—");

    // -------------------------------
    // CONNECTION STATE
    // -------------------------------
    setConn("LIVE");
    document.body.classList.add("nexus-live");
    document.body.classList.remove("nexus-offline");

  } catch (err) {
    console.warn("❌ NEXUS backend unreachable:", err);

    setConn("OFFLINE");
    setText("fleet", "OFFLINE / DEMO");
    setText("reasoning", "Backend not reachable.");

    document.body.classList.add("nexus-offline");
    document.body.classList.remove("nexus-live");
  }
}

// =====================================================
// START
// =====================================================
tick();
setInterval(tick, POLL_INTERVAL_MS);
