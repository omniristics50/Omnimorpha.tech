from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import random

app = FastAPI(title="NEXUS Demo API", version="0.1")

# Allow local dev + your domain (adjust later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://omnimorpha.tech",
        "https://www.omnimorpha.tech",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/v1/state")
def state():
    # Simple simulated digital twin values
    soc = random.randint(42, 96)
    temp = round(random.uniform(26.0, 48.0), 1)
    health = random.randint(78, 99)

    risk = min(100, max(0, int((temp - 25) * 2 + (95 - soc) * 0.6 + random.uniform(-3, 3))))
    tier = "GREEN" if risk < 25 else "AMBER" if risk < 55 else "RED"

    strategies = [
        {
            "title": "Reduce thermal load",
            "why": "Temperature drift sustained; prioritize cooling window to stabilize risk.",
            "impact": "-12 risk"
        },
        {
            "title": "Smooth discharge profile",
            "why": "High variance increases stress proxies; steady draw improves stability.",
            "impact": "-7 risk"
        },
        {
            "title": "Recalibrate thresholds",
            "why": "Validation prefers persistence; tuning reduces false alarms.",
            "impact": "↓ false alarms"
        },
    ]

    timeline = [
        {"time": "now", "title": f"Risk tier: {tier}", "text": "Kernel updated telemetry + risk inference."},
        {"time": "now", "title": "Validation", "text": "Persistence window applied to avoid noisy alerts."},
        {"time": "now", "title": "Strategy ranked", "text": f"Top: {strategies[0]['title']}."},
    ]

    return {
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
        "telemetry": {
            "soc": soc,
            "temp_c": temp,
            "voltage": round(random.uniform(3.6, 4.1), 2),
            "current_a": round(random.uniform(-22, 18), 1),
            "cycle_count": random.randint(120, 980),
            "impedance_proxy": round(random.uniform(0.012, 0.040), 3),
            "temp_trend": "rising" if temp > 38 else "stable",
        },
        "health": {"index": health, "degradation": "low" if health > 90 else "moderate"},
        "risk": {"score": risk, "confidence": "high" if risk > 30 else "medium"},
        "fleet": {"status": "SINGLE INSTANCE"},
        "strategies": strategies,
        "explain": {
            "narrative": f"Risk {tier} due to temperature ({temp}°C) and SOC ({soc}%). Validation applied to reduce false alarms.",
            "drivers": ["thermal drift", "SOC variance", "impedance proxy"],
        },
        "timeline": timeline,
    }
