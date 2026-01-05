from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
import math
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP_TITLE = "NEXUS Demo API"
APP_VERSION = "0.2.1"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# CORS: allow your website + common local dev ports
allowed_origins = [
    "https://omnimorpha.tech",
    "https://www.omnimorpha.tech",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))

def risk_tier(score: float) -> str:
    if score < 25:
        return "GREEN"
    if score < 55:
        return "AMBER"
    return "RED"

def trend_label(delta: float, deadband: float = 0.15) -> str:
    if delta > deadband:
        return "rising"
    if delta < -deadband:
        return "falling"
    return "stable"

# Simple in-memory “state” to make values evolve smoothly between calls.
_state = {
    "t": 0.0,
    "soc": 78.0,
    "temp": 34.0,
    "voltage": 3.92,
    "current": -6.0,
    "cycle_count": 420,
    "impedance": 0.022,
    "health": 94.0,
    "last_temp": 34.0,
}

def step_simulation() -> Dict[str, Any]:
    """Advance simulated digital twin by one tick."""
    _state["t"] += 1.0
    t = _state["t"]

    base_soc = _state["soc"] + (math.sin(t / 10.0) * 0.4) + random.uniform(-0.25, 0.25)
    base_temp = _state["temp"] + (math.sin(t / 12.0) * 0.35) + random.uniform(-0.2, 0.2)

    current = _state["current"] + (math.sin(t / 8.0) * 0.8) + random.uniform(-0.6, 0.6)
    temp = base_temp + (abs(current) * 0.03)

    soc = clamp(base_soc, 35.0, 98.0)
    temp = clamp(temp, 24.0, 58.0)

    voltage = clamp(3.55 + (soc / 100.0) * 0.65 + random.uniform(-0.02, 0.02), 3.45, 4.20)

    impedance = clamp(_state["impedance"] + random.uniform(-0.0002, 0.00035), 0.010, 0.055)

    cycle_count = int(_state["cycle_count"] + random.randint(0, 1))
    health = clamp(_state["health"] - (0.0012 if cycle_count % 10 == 0 else 0.0), 70.0, 99.0)

    temp_delta = temp - _state["last_temp"]
    temp_tr = trend_label(temp_delta)

    _state.update(
        soc=soc,
        temp=temp,
        voltage=voltage,
        current=current,
        cycle_count=cycle_count,
        impedance=impedance,
        health=health,
        last_temp=temp,
    )

    return {
        "soc": round(soc, 0),
        "temp_c": round(temp, 1),
        "temp_trend": temp_tr,
        "voltage": round(voltage, 2),
        "current_a": round(current, 1),
        "cycle_count": cycle_count,
        "impedance_proxy": round(impedance, 3),
        "health_index": round(health, 0),
    }

def compute_risk(telemetry: Dict[str, Any]) -> Dict[str, Any]:
    """Compute investor-safe risk score with dampened spikes."""
    soc = telemetry["soc"]
    temp = telemetry["temp_c"]
    imp = telemetry["impedance_proxy"]

    temp_risk = clamp((temp - 28.0) * 2.2, 0, 70)
    soc_risk = clamp((55.0 - soc) * 0.7, 0, 25)
    imp_risk = clamp((imp - 0.018) * 900.0, 0, 35)

    raw = temp_risk + soc_risk + imp_risk
    damp = 0.86 if temp > 40 else 0.92
    score = clamp(raw * damp, 0, 100)

    tier = risk_tier(score)
    confidence = "high" if score >= 45 else "medium" if score >= 25 else "low"

    drivers: List[str] = []
    if temp > 40:
        drivers.append("thermal drift")
    elif temp > 34:
        drivers.append("elevated temperature")
    if soc < 55:
        drivers.append("low SOC stress proxy")
    if imp > 0.030:
        drivers.append("impedance aging proxy")
    elif imp > 0.022:
        drivers.append("impedance variance")
    if not drivers:
        drivers = ["stable telemetry"]

    narrative = (
        f"Risk tier {tier}. Temperature {temp}°C, SOC {soc}%, impedance proxy {imp}. "
        f"Validation dampens transient spikes to reduce false alarms."
    )

    return {
        "score": int(round(score)),
        "tier": tier,
        "confidence": confidence,
        "drivers": drivers,
        "narrative": narrative,
    }

def generate_strategies(risk: Dict[str, Any], telemetry: Dict[str, Any]) -> List[Dict[str, str]]:
    """Recommendation-only strategies (no execution)."""
    score = risk["score"]
    temp = telemetry["temp_c"]
    soc = telemetry["soc"]
    imp = telemetry["impedance_proxy"]

    strategies: List[Dict[str, str]] = []

    if temp >= 42:
        strategies.append({
            "title": "Reduce thermal load window",
            "why": "Sustained elevated temperature is the top driver; stabilize thermal conditions first.",
            "impact": "-12 risk (est.)"
        })
    elif temp >= 35:
        strategies.append({
            "title": "Schedule cooling stabilization interval",
            "why": "Temperature is above baseline; stabilize to keep risk low and preserve health.",
            "impact": "-7 risk (est.)"
        })

    if soc <= 55:
        strategies.append({
            "title": "Smooth discharge profile",
            "why": "Low SOC stress proxy detected; smoother draw reduces volatility and improves confidence.",
            "impact": "-5 risk (est.)"
        })

    if imp >= 0.030:
        strategies.append({
            "title": "Adjust operating envelope (aging-aware)",
            "why": "Impedance proxy suggests aging; recommend conservative envelope to reduce long-term stress.",
            "impact": "health preservation"
        })
    elif imp >= 0.022:
        strategies.append({
            "title": "Increase validation persistence window",
            "why": "Impedance variance can create noise; persistence reduces false alarms and improves stability.",
            "impact": "↓ false alarms"
        })

    strategies.append({
        "title": "Emit audit record + explainability note",
        "why": "Maintain a readable, traceable narrative for investors and operators (read-only).",
        "impact": "audit-ready"
    })

    if score < 25:
        strategies.insert(0, {
            "title": "Maintain baseline monitoring cadence",
            "why": "Telemetry appears stable; continue normal monitoring and memory logging.",
            "impact": "stable"
        })

    return strategies[:5]

def build_timeline(risk: Dict[str, Any], strategies: List[Dict[str, str]]) -> List[Dict[str, str]]:
    tier = risk["tier"]
    top = strategies[0]["title"] if strategies else "—"
    now = utc_now_iso()
    return [
        {"time": now, "title": f"Kernel tick — {tier}", "text": "Telemetry ingested; validation guards applied."},
        {"time": now, "title": "Risk inference", "text": risk["narrative"]},
        {"time": now, "title": "Strategy ranked", "text": f"Top recommendation: {top} (recommendation only)."},
    ]

# -----------------------------------------------------------------------------
# Routes (THIS is what stops the 404s you saw in Render logs)
# -----------------------------------------------------------------------------

@app.get("/")
def root() -> Dict[str, str]:
    # Render/browsers often ping "/" – this prevents noisy 404 logs.
    return {"service": "nexus-backend", "status": "ok", "time": utc_now_iso()}

@app.get("/healthz")
def healthz() -> Dict[str, str]:
    # Simple health endpoint (also prevents 404s).
    return {"status": "ok", "time": utc_now_iso()}

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.get("/v1/state")
def v1_state() -> Dict[str, Any]:
    telemetry = step_simulation()
    risk = compute_risk(telemetry)
    strategies = generate_strategies(risk, telemetry)
    timeline = build_timeline(risk, strategies)

    return {
        "meta": {"timestamp": utc_now_iso(), "version": APP_VERSION},
        "telemetry": {
            "soc": telemetry["soc"],
            "temp_c": telemetry["temp_c"],
            "temp_trend": telemetry["temp_trend"],
            "voltage": telemetry["voltage"],
            "current_a": telemetry["current_a"],
            "cycle_count": telemetry["cycle_count"],
            "impedance_proxy": telemetry["impedance_proxy"],
        },
        "health": {
            "index": telemetry["health_index"],
            "degradation": "low" if telemetry["health_index"] >= 90 else "moderate",
        },
        "risk": {
            "score": risk["score"],
            "tier": risk["tier"],
            "confidence": risk["confidence"],
        },
        "fleet": {"status": "SINGLE INSTANCE", "count": 1},
        "strategies": strategies,
        "explain": {
            "narrative": risk["narrative"],
            "drivers": risk["drivers"],
        },
        "timeline": timeline,
        "governance": {
            "mode": "READ_ONLY",
            "audit": "ENABLED",
            "execution": "DISABLED",
        },
    }

@app.get("/v1/risk")
def v1_risk() -> Dict[str, Any]:
    telemetry = step_simulation()
    risk = compute_risk(telemetry)
    return {"meta": {"timestamp": utc_now_iso(), "version": APP_VERSION}, "risk": risk}

@app.get("/v1/strategies")
def v1_strategies() -> Dict[str, Any]:
    telemetry = step_simulation()
    risk = compute_risk(telemetry)
    strategies = generate_strategies(risk, telemetry)
    return {"meta": {"timestamp": utc_now_iso(), "version": APP_VERSION}, "strategies": strategies}

@app.get("/v1/timeline")
def v1_timeline() -> Dict[str, Any]:
    telemetry = step_simulation()
    risk = compute_risk(telemetry)
    strategies = generate_strategies(risk, telemetry)
    timeline = build_timeline(risk, strategies)
    return {"meta": {"timestamp": utc_now_iso(), "version": APP_VERSION}, "timeline": timeline}
