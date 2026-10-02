"""Alur Must M2: deteksi taktik tekanan pada teks percakapan.

Versi walking skeleton: berbasis kata kunci (stub yang dapat dijelaskan).
Jika ANTHROPIC_API_KEY tersedia, llm_tactics() dapat dipakai sebagai pengganti
(belum diuji pada skeleton ini; lihat blueprint bagian Pendekatan AI).
"""
import os
import re
from .pii import mask_pii

# (kode, label, bobot, pola)
PATTERNS = [
    ("DESAK_TRANSFER", "Mendesak transfer segera", 10,
     r"segera|buruan|cepat transfer|sekarang juga|hari ini juga|keburu habis|tinggal \d+ (?:unit|pcs)|stok terakhir"),
    ("TOLAK_REKBER", "Menolak rekening bersama/COD", 15,
     r"tanpa rekber|ga(?:k)? pakai rekber|nggak pakai rekber|tidak (?:pakai|menerima) rekber|no rekber|tidak bisa cod|ga(?:k)? bisa cod|transfer langsung"),
    ("PINDAH_KANAL", "Memindahkan percakapan ke kanal lain", 8,
     r"pindah (?:ke )?wa|lanjut (?:di )?wa|chat (?:aja )?(?:di )?wa|hubungi (?:saya )?(?:di )?(?:wa|telegram)|dm aja|lanjut telegram"),
    ("TRANSFER_DULU", "Meminta bayar penuh/DP sebelum barang dilihat", 10,
     r"dp dulu|bayar dulu|transfer dulu|lunas dulu|booking fee|uang muka"),
    ("MINTA_OTP", "Meminta kode OTP/data sensitif", 30,
     r"kode otp|otp|pin (?:atm|m-banking)|password|kode verifikasi"),
    ("QR_LUAR", "Mengarahkan pembayaran ke QR/tautan di luar platform", 12,
     r"scan qr|kode qr|qris pribadi|link pembayaran|klik tautan"),
]
MAX_CHAT_POINTS = 40


def detect_tactics(text: str) -> list[dict]:
    found = []
    low = text.lower()
    for code, label, weight, pattern in PATTERNS:
        m = re.search(pattern, low)
        if m:
            found.append({"code": code, "label": label, "points": weight, "evidence": m.group(0)})
    return found


def llm_tactics(text: str) -> list[dict] | None:
    """Opsional: klasifikasi taktik dengan LLM. Mengembalikan None bila tidak tersedia."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        return None
    import json
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=("Kamu pendeteksi taktik penipuan. Dari percakapan jual-beli, kembalikan JSON array "
                "berisi kode dari: " + ", ".join(p[0] for p in PATTERNS) + ". Hanya JSON."),
        messages=[{"role": "user", "content": mask_pii(text)}],
    )
    try:
        codes = json.loads(msg.content[0].text)
    except Exception:
        return None
    return [{"code": c, "label": l, "points": w, "evidence": "(LLM)"}
            for c, l, w, _ in PATTERNS if c in codes]
