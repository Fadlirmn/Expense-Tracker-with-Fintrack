# Decision Log

## 1. Unified Telegram Bot Integration
- **Decision:** Replace the Python bot client with a Flask REST API server exposing a `/scan` endpoint, and delegate all bot event handling to FinTrack's Go `bot-gateway`.
- **Rationale:** Minimizes system footprint on the Home Server by avoiding running two separate Telegram bots concurrently. Simplifies user experience by providing a single bot interface for both manual tracking and receipt scans.
- **Alternative Considered:** Keep both bots running on different tokens. Rejected because it is redundant and harder for the user to maintain.

## 2. Docker Bridge Network & Internal URL Routing
- **Decision:** Run the newly created `expense-tracker-api` on the existing attachable `fintrack-network` and route bot-gateway requests to `http://expense-tracker-api:8000`.
- **Rationale:** Ensures direct container-to-container communication without exposing the port publicly to the host or internet, maintaining security and fast response times.
