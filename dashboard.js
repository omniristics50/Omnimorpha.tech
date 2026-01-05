console.log("✅ dashboard.js loaded");

const API_BASE = "https://omnimorpha-tech.onrender.com"; // later: https://api.omnimorpha.tech
const POLL_INTERVAL_MS = 2500;

const params = new URLSearchParams(window.location.search);
const MODE = (params.get("mode") || "live").toLowerCase(); // "live" or "investor"

const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "—";
};

const setConn = (text) => {
  const el = document.getElementById("connectionText");
  if (el) el.textContent = text;
};

async function fetchJSON(path) {
  const url = `${API_BASE}${path}?mode=${encodeURIComponent(MODE)}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function tick() {
  try {
    const state = await fetchJSON("/v1/state");

    setText("health", state?.health?.index != null ? `${state.health.index}%` : "—");
    setText("risk", state?.risk?.score != null ? `${state.risk.score}/100` : "—");
    setText("fleet", state?.fleet?.status ?? "SINGLE INSTANCE");

    const top = state?.strategies?.[0];
    setText("topStrategy", top?.title ?? "—");
    setText("reasoning", state?.explain?.narrative ?? "—");

    setConn(MODE === "investor" ? "INVESTOR" : "LIVE");
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

tick();
setInterval(tick, POLL_INTERVAL_MS);
