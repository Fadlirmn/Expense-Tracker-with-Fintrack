# Analisis Flow & Rencana Deploy Home Server

**Tanggal:** 2026-06-26  
**Status:** selesai  
**Versi:** v12

## Konteks
Analisis alur kode Expense Tracker Agent dan implementasi Dockerization serta integrasi Telegram Bot & FinTrack untuk deploy di home server.

## Keputusan & Hasil
- **Dockerization & Network:** Kontainer dashboard dan bot terhubung ke external network `fintrack-network` agar dapat berkomunikasi langsung dengan `http://fintrack-api:8080`.
- **Integrasi & Refaktoring FinTrack:**
  - Membuat modul `src/fintrack_client.py` untuk mengeliminasi duplikasi kode HTTP client.
  - `bot.py` mencocokkan chat ID Telegram ke FinTrack user UUID (`get_user_id_by_chat_id()`) lalu mengirim transaksi (`create_transaction()`) otomatis dengan API Key.
  - `app.py` menyinkronkan pengeluaran dari upload Streamlit jika `DEFAULT_FINTRACK_USER_ID` diset di `.env`.
- **Dokumentasi & Setup:** Mengupdate `README.md` dengan instruksi instalasi Docker, parameter `.env` baru, dan skema arsitektur integrasi.
- **Kredensial Validation:** Menambahkan pendeteksian dan pesan kesalahan yang ramah pada `bot.py` jika pengguna lupa mengisi variabel kredensial Telegram asli di `.env` (mencegah crash traceback).

## Tindak Lanjut
- [ ] User mengonfigurasi API key dan token Telegram asli di berkas `.env` lalu menjalankan kontainer.

---
*Dibuat otomatis oleh agent · maks. 200 kata*
