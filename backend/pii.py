"""Penyamaran data pribadi (fitur Should S2) sebelum teks dikirim ke layanan eksternal."""
import re

_PHONE = re.compile(r"(?<!\d)(?:\+62|62|0)8\d{8,11}(?!\d)")
_ACCOUNT = re.compile(r"(?<!\d)\d{10,16}(?!\d)")


def mask_pii(text: str) -> str:
    text = _PHONE.sub("[NOMOR_HP]", text)
    return _ACCOUNT.sub("[NOMOR_REKENING]", text)
