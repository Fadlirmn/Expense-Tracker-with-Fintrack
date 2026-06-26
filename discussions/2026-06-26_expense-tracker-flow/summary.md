# Integrasi Telegram Bot FinTrack & OCR Expense Tracker

**Tanggal:** 2026-06-26  
**Status:** selesai  
**Versi:** v14

## Konteks
Penyatuan Telegram bot agar pengguna dapat mengirim foto struk ke bot FinTrack untuk diproses OCR/LLM via API Expense Tracker dan dicatat ke FinTrack otomatis.

## Keputusan & Hasil
- **Expense Tracker API:** Membuat Flask server (`api.py`) port 8000 dengan endpoint `/scan` untuk OCR (Tesseract) & LLM parsing (Llama 3).
- **FinTrack Bot Gateway:** Mengubah Go handler (`handler.go`) untuk memproses pesan gambar, mengunduh file, mengirimkannya ke API, lalu memanggil `SaveTransaction` untuk menyimpan data.
- **Pembaruan Panduan:** Memperbarui menu bantuan (`guideText`) di Telegram bot untuk menginstruksikan pengguna cara mengirim foto struk secara langsung.
- **Docker Network:** Menambahkan parameter `EXPENSE_TRACKER_API_URL` ke `bot-gateway` di FinTrack `docker-compose.yml`.

## Tindak Lanjut
- [ ] Bangun ulang kontainer pada kedua repositori menggunakan `docker compose up -d --build`.
- [ ] Kirim foto struk belanja ke bot Telegram FinTrack untuk uji coba.

---
*Dibuat otomatis oleh agent · maks. 200 kata*
