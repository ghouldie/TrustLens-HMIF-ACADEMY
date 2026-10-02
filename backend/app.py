from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .scoring import assess, check_account, check_price, check_profile
from .tactics import detect_tactics

app = FastAPI(title="TrustLens API", version="0.1.0")
FRONT = Path(__file__).parent.parent / "frontend"


class Payload(BaseModel):
    account: str | None = None
    price: int | None = None
    category: str | None = None
    account_age_days: int | None = None
    followers: int | None = None
    chat_text: str | None = None


@app.post("/api/assess")
def api_assess(p: Payload):
    return assess(p.model_dump())


@app.post("/api/profile-check")  # Alur Must M1
def api_profile(p: Payload):
    return {k: v for k, v in {
        "rekening": check_account(p.account),
        "harga": check_price(p.category, p.price),
        "profil": check_profile(p.account_age_days, p.followers)}.items() if v}


@app.post("/api/chat-analyze")  # Alur Must M2
def api_chat(p: Payload):
    return {"tactics": detect_tactics(p.chat_text or "")}


@app.get("/")
def index():
    return FileResponse(FRONT / "index.html")


app.mount("/static", StaticFiles(directory=FRONT), name="static")
