# Analisis Flow & Rencana Deploy Home Server

**Tanggal:** 2026-06-26  
**Status:** selesai  
**Versi:** v11

## Konteks
Analisis alur kode Expense Tracker Agent dan implementasi Dockerization serta integrasi Telegram Bot & FinTrack untuk deploy di home server.

## Keputusan & Hasil
- **Dockerization & Network:** Kontainer dashboard dan bot terhubung ke external network `fintrack-network` agar dapat berkomunikasi langsung dengan `http://fintrack-api:8080`.
- **Integrasi & Refaktoring FinTrack:**
  - Membuat modul `src/fintrack_client.py` untuk mengeliminasi duplikasi kode HTTP client.
  - `bot.py` mencocokkan chat ID Telegram ke FinTrack user UUID (`get_user_id_by_chat_id()`) lalu mengirim transaksi (`create_transaction()`) otomatis dengan API Key.
  - `app.py` menyinkronkan pengeluaran dari upload Streamlit jika `DEFAULT_FINTRACK_USER_ID` diset di `.env`.
- **Dokumentasi & Setup:** Mengupdate `README.md` dengan instruksi instalasi Docker, parameter `.env` baru, dan skema arsitektur integrasi.
- **Docker Build Fix:** Memperbaiki kegagalan instalasi `libgl1-mesa-glx` pada Debian slim dengan mengganti dependency python ke `opencv-python-headless` (menghapus GUI dependencies) serta mendegradasi library OpenGL ke `libgl1` pada `Dockerfile`.

## Tindak Lanjut
- [ ] User melakukan pembangunan ulang container dengan `docker compose up -d --build`.

---
*Dibuat otomatis oleh agent · maks. 200 kata*
