# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `api.py` (Why: Exposes a Flask REST API on port 8000 for receipt scanning, allowing the FinTrack Telegram bot gateway to query OCR & LLM parsing internally).

### Changed
- `docker-compose.yml` (Why: Replaced the obsolete `telegram-bot` service with `expense-tracker-api` to run `api.py`).
- `requirements.txt` (Why: Added `Flask` dependency to run the REST API server).
