# Project Context: Expense Tracker Agent

## Project Overview

This project is an intelligent expense tracker that processes images of receipts. It uses Optical Character Recognition (OCR) to digitize the receipt, then leverages Large Language Models (LLMs) via the Groq API to extract structured data and provide financial analysis. The application supports a user-friendly Streamlit web interface as well as a convenient Telegram Bot interface for scanning receipts on-the-go.

It also integrates seamlessly with the **FinTrack** ecosystem to automatically synchronize scanned expenses with your personal finance dashboard.

The core pipeline is as follows:

1.  **Image Upload / Scan**: The user uploads a receipt image via the Streamlit web UI or sends a photo directly to the Telegram Bot.
2.  **OCR Processing**: The image is pre-processed (grayscale, thresholding) with OpenCV and scanned by Tesseract OCR to extract raw text (platform-agnostic config).
3.  **Structured Data Extraction**: The raw text is sent to a Groq Llama 3 model, which returns a clean JSON object containing the merchant, date, total, currency, category, and line items.
4.  **Financial Analysis**: The structured data is passed to a second LLM agent (Groq Llama 3) which analyzes the spending and provides a concise, human-like summary.
5.  **FinTrack Synchronization**: If configured, the transaction is automatically sent to your FinTrack backend API.
6.  **Local Logging**: The extracted data is appended to `data/expenses_log.json` for persistent dashboard storage.

---

## Interfaces

### 1. Streamlit Web Dashboard
Provides visual monthly metrics, expense category bar charts, and a detailed transaction history table.
*   **Run command**: `streamlit run app.py`

### 2. Telegram Bot Interface
Enables receipt scanning on-the-go. Users simply snap a photo of a receipt and send it to the bot.
*   **Run command**: `python bot.py`
*   **Security**: Secured via user ID whitelist in `.env` (`ALLOWED_TELEGRAM_USER_IDS`).

---

## Integration with FinTrack
The Expense Tracker Agent integrates with the **FinTrack** backend Go API via internal endpoints:
- **Telegram Bot Sync**: Bot queries `GET /internal/v1/binding` using the sender's Telegram chat ID to find their FinTrack User UUID. If found, it automatically posts the transaction via `POST /internal/v1/transactions`.
- **Dashboard Web Sync**: Automatically syncs web-uploaded transactions to a default User UUID specified via `DEFAULT_FINTRACK_USER_ID` in `.env`.
- All inter-service communications are secured with a shared API key (`X-API-Key` header).

---

## Building and Running

### 1. Prerequisites
- Python 3.10+
- Tesseract OCR Engine:
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`
  - **Windows**: Install and add to system PATH.

### 2. Setup environment variables
Create a `.env` file in the root of the project directory based on `.env.example`:
```env
# Groq API Configuration
GROQ_API_KEY="your_groq_api_key"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
ALLOWED_TELEGRAM_USER_IDS="12345678,98765432"

# FinTrack Integration (Optional)
FINTRACK_API_URL="http://fintrack-api:8080" # internal docker container name
FINTRACK_API_KEY="your_shared_gateway_api_key"
DEFAULT_FINTRACK_USER_ID="your_fintrack_user_uuid"
```

### 3. Native Installation (Optional)
It is recommended to use a virtual environment.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Running with Docker Compose (Recommended)
This application can be deployed on a home server as a multi-container Docker application linked directly to the `fintrack-network`.

Run the following command to build and launch both the dashboard and the Telegram bot:
```bash
docker compose up --build -d
```
Containers deployed:
- `expense_tracker_dashboard`: Serves the Streamlit UI on port `8501`.
- `expense_tracker_bot`: Runs the Telegram bot daemon in the background.

Both containers share the `./data` directory as a mounted volume to keep database logs (`data/expenses_log.json`) and temporary uploads synchronized.
