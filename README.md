# TrustLens
Asisten AI penilai risiko penjual sebelum transfer (HMIF Academy, Kelompok 1 – Nonactives).

## Menjalankan (3 langkah)
```bash
pip install -r requirements.txt
python run.py
# buka http://127.0.0.1:8000
```
Contoh input/output: folder `/demo`. Uji otomatis: `python -m pytest`.

## Dua alur Must yang berjalan
- M1 Cek rekening, harga, profil: `POST /api/profile-check`
- M2 Analisis taktik tekanan pada percakapan: `POST /api/chat-analyze`
- Gabungan skor + alasan + langkah aman: `POST /api/assess`

## Status jujur
Komponen AI masih berbasis aturan (stub) dan data dummy. Klasifikasi LLM opsional
(`ANTHROPIC_API_KEY`) belum diuji. Lihat `demo/input_gagal.json` untuk contoh kegagalan.

## Alur Git
`main` (stabil) ← `develop` ← `feat/<nama>`; setiap PR ditinjau minimal satu anggota.
Pesan commit: `feat:`, `fix:`, `docs:`, `test:`.
