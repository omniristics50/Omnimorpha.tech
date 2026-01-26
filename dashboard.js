console.log("✅ dashboard.js loaded");

// =====================================================
// CONFIG
// =====================================================
const API_BASE = "https://api.omnimorpha.tech";
const POLL_INTERVAL_MS = 2500;

// 👉 ADD THESE TWO LINES RIGHT HERE
const params = new URLSearchParams(window.location.search);
const MODE = (params.get("mode") || "live").toLowerCase();

// =====================================================
// DOM HELPERS
// =====================================================
const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "—";
};

const setTimeline = (items) => {
  const ul = document.getElementById("timeline");
  if (!ul) return;

  ul.innerHTML = "";
  const list = Array.isArray(items) && items.length ? items : [];

  if (!list.length) {
    const li = document.createElement("li");
    li.textContent = "—";
    ul.appendChild(li);
    return;
  }

  list.slice(0, 6).forEach((e) => {
    const li = document.createElement("li");
    const t = e?.time ? `${e.time} — ` : "";
    const title = e?.title ?? "";
    const text = e?.text ? `: ${e.text}` : "";
    li.textContent = `${t}${title}${text}`.trim();
    ul.appendChild(li);
  });
};

async function fetchJSON(path) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function tick() {
  try {
    const state = await fetchJSON("/v1/state");

    // KPIs
    setText("health", state?.health?.index != null ? `${state.health.index}%` : "—");
    setText("risk", state?.risk?.score != null ? `${state.risk.score}/100` : "—");
    setText("fleet", state?.fleet?.status ?? "SINGLE INSTANCE");

    const top = state?.strategies?.[0];
    setText("topStrategy", top?.title ?? "—");
    setText("reasoning", state?.explain?.narrative ?? "—");

    // ✅ STATUS SET HERE (correct)
    setConn(MODE === "investor" ? "INVESTOR" : "LIVE");

  } catch (err) {
    // ❌ OFFLINE STATE
    setConn("OFFLINE");
  }
}

    // AI Summary (short, readable)
    const tier = state?.risk?.tier ?? "";
    const score = state?.risk?.score != null ? `${state.risk.score}/100` : "";
    const temp = state?.telemetry?.temp_c != null ? `${state.telemetry.temp_c}°C` : "—";
    const soc = state?.telemetry?.soc != null ? `${state.telemetry.soc}%` : "—";
    const summary =
      tier && score
        ? `Current risk is ${tier} (${score}). Temperature ${temp}, SOC ${soc}. Top recommendation: ${top?.title ?? "—"}.`
        : (state?.explain?.narrative ?? "—");
    setText("summary", summary);

    // Timeline feed
    setTimeline(state?.timeline ?? []);

    // Status
    setConn("LIVE");
    document.body.classList.add("nexus-live");
    document.body.classList.remove("nexus-offline");
  } catch (err) {
    console.warn("❌ NEXUS offline:", err);

    setConn("OFFLINE");
    setText("fleet", "OFFLINE / DEMO");
    setText("summary", "Backend not reachable.");
    setText("reasoning", "Backend not reachable.");
    setTimeline([]);

    document.body.classList.add("nexus-offline");
    document.body.classList.remove("nexus-live");
  }
}

tick(); 
setInterval(tick, POLL_INTERVAL_MS);
