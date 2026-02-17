from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

app = FastAPI()

# Allow your website to fetch it (we can lock this down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

LATEST = Path("latest.json")

@app.get("/")
def root():
    return {"ok": True, "service": "regent-pulse"}

@app.get("/latest.json")
def latest():
    if not LATEST.exists():
        return {"ok": False, "message": "no data yet"}
    return json.loads(LATEST.read_text(encoding="utf-8"))

@app.post("/push")
async def push(payload: dict):
    LATEST.write_text(json.dumps(payload), encoding="utf-8")
    return {"ok": True}
