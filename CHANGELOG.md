# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `src/wol.py` (Why: Wakes the remote Ryzen Ollama server using UDP broadcast Wake-on-LAN packets).
- `api.py` (Why: Exposes a Flask REST API on port 8000 for receipt scanning, allowing the FinTrack Telegram bot gateway to query OCR & LLM parsing internally).

### Changed
- `src/extractor.py` (Why: Rewrote parsing module to query local Ollama LLM on port 11435 instead of Groq).
- `src/analysis_engine.py` (Why: Rewrote narrative analysis to use local Ollama LLM on port 11435 instead of Groq).
- `src/config.py` (Why: Added Ollama and Ryzen config parsing functions).
- `.env.example` (Why: Documented Ollama and Ryzen node configuration variables).
- `docker-compose.yml` (Why: Replaced the obsolete `telegram-bot` service with `expense-tracker-api` to run `api.py`).
- `requirements.txt` (Why: Added `Flask` dependency to run the REST API server).
