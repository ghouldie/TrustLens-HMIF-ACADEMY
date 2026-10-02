"""Alur Must M1: cek rekening, harga, dan profil; lalu agregasi skor risiko."""
import json
from pathlib import Path
from .tactics import detect_tactics, llm_tactics, MAX_CHAT_POINTS

DATA = Path(__file__).parent / "data"
REPORTED = json.loads((DATA / "reported_accounts.json").read_text(encoding="utf-8"))
PRICES = json.loads((DATA / "price_reference.json").read_text(encoding="utf-8"))


def check_account(account):
    if not account:
        return None
    hit = REPORTED.get(account.strip())
    if hit:
        return {"signal": "REKENING_DILAPORKAN", "points": 45,
                "label": f"Rekening pernah dilaporkan {hit['reports']} kali ({hit['category']})"}
    return {"signal": "REKENING_BERSIH", "points": 0,
            "label": "Rekening tidak ditemukan di data laporan (bukan jaminan aman)"}


def check_price(category, price):
    if not category or not price:
        return None
    ref = PRICES.get(category.strip().lower())
    if not ref:
        return {"signal": "HARGA_TAK_DIKETAHUI", "points": 0,
                "label": "Kategori belum punya harga acuan"}
    ratio = price / ref
    if ratio < 0.4:
        return {"signal": "HARGA_JAUH_DI_BAWAH", "points": 30,
                "label": f"Harga hanya {ratio:.0%} dari median acuan"}
    if ratio < 0.6:
        return {"signal": "HARGA_DI_BAWAH", "points": 20,
                "label": f"Harga {ratio:.0%} dari median acuan"}
    return {"signal": "HARGA_WAJAR", "points": 0, "label": f"Harga {ratio:.0%} dari median acuan (wajar)"}


def check_profile(age_days, followers):
    if age_days is None:
        return None
    pts, notes = 0, []
    if age_days < 30:
        pts += 10
        notes.append(f"akun baru ({age_days} hari)")
    if followers is not None and followers > 5000 and age_days < 90:
        pts += 8
        notes.append("pengikut banyak untuk akun semuda ini")
    return {"signal": "PROFIL", "points": pts,
            "label": "Profil: " + (", ".join(notes) if notes else "tidak ada keanehan terdeteksi")}


def level(score):
    return "Rendah" if score < 30 else "Sedang" if score < 60 else "Tinggi"


SAFE_STEPS = {
    "Tinggi": ["Jangan transfer sekarang.", "Minta transaksi lewat rekening bersama atau COD.",
               "Minta video call menunjukkan barang.", "Jika sudah terlanjur, hubungi bank dan lapor ke IASC."],
    "Sedang": ["Minta bukti tambahan (foto/video terbaru dengan tulisan tanggal).",
               "Usulkan rekening bersama; perhatikan reaksi penjual.", "Bayar bertahap hanya jika barang sudah terlihat."],
    "Rendah": ["Tetap simpan bukti percakapan dan transfer.", "Hindari membagikan kode OTP atau PIN kepada siapa pun."],
}


def assess(data: dict) -> dict:
    chat = data.get("chat_text") or ""
    tactics = (llm_tactics(chat) or detect_tactics(chat)) if chat else []
    chat_pts = min(MAX_CHAT_POINTS, sum(t["points"] for t in tactics))
    groups = {
        "rekening": check_account(data.get("account")),
        "harga": check_price(data.get("category"), data.get("price")),
        "profil": check_profile(data.get("account_age_days"), data.get("followers")),
        "chat": ({"signal": "TAKTIK_CHAT", "points": chat_pts,
                  "label": "Percakapan: " + (", ".join(t["label"] for t in tactics) if tactics else "tidak ada taktik tekanan terdeteksi")}
                 if chat else None),
    }
    used = {k: v for k, v in groups.items() if v}
    score = min(100, sum(v["points"] for v in used.values()))
    confidence = round(min(0.90, 0.25 + 0.15 * len(used)), 2) if used else 0.0
    lvl = level(score)
    return {
        "score": score, "level": lvl, "confidence": confidence,
        "reasons": [v["label"] for v in used.values() if v["points"] > 0] or ["Tidak ada sinyal risiko pada data yang diberikan"],
        "signals": used, "tactics": tactics,
        "missing_inputs": [k for k, v in groups.items() if not v],
        "safe_steps": SAFE_STEPS[lvl],
        "disclaimer": "Skor adalah perkiraan, bukan vonis. Keputusan akhir ada pada Anda.",
    }
