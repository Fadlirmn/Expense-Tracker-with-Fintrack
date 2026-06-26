# Changelog — Analisis Flow Expense Tracker

| Tanggal | Versi | Perubahan |
|---------|-------|-----------|
| 2026-06-26 | v1 | Dibuat pertama kali |
| 2026-06-26 | v2 | Rencana implementasi Docker dan komparasi bot Telegram/WhatsApp |
| 2026-06-26 | v3 | Implementasi penuh Dockerfile, docker-compose, bot.py, perbaikan ocr_engine.py dan app.py |
| 2026-06-26 | v4 | Pembuatan berkas template .env.example untuk panduan pengisian kredensial secara aman |
| 2026-06-26 | v5 | Implementasi integrasi penuh dengan FinTrack REST API via HTTP client di bot.py dan app.py, serta penyelarasan external Docker network |
| 2026-06-26 | v6 | Refaktoring modul API client FinTrack ke src/fintrack_client.py, pembersihan redundansi, dan pembuatan Git commit lokal `c312b9d` |
| 2026-06-26 | v7 | Pembaruan README.md dengan dokumentasi integrasi Telegram, Docker Compose, dan FinTrack |
| 2026-06-26 | v8 | Penambahan panduan pengalihan git remote origin ke repositori pribadi pengguna |
| 2026-06-26 | v9 | Pembersihan berkas .env yang tidak sengaja terkomit di riwayat Git lawas untuk mem-bypass penolakan push GitHub |
| 2026-06-26 | v10 | Pengecekan dan sinkronisasi push pada repositori FinTrack (`Fadlirmn/Fintrack.git`) |
| 2026-06-26 | v11 | Perbaikan kegagalan pembangunan image Docker akibat hilangnya package libgl1-mesa-glx dengan menggunakan opencv-python-headless and libgl1 |
| 2026-06-26 | v12 | Penambahan validasi deteksi placeholder kredensial di bot.py untuk memberikan pesan error yang informatif |
| 2026-06-26 | v13 | Penyatuan Telegram Bot dengan FinTrack, penambahan api.py, penyelarasan docker-compose, dan webhook handler Go |
