"""
analysis_engine.py — Agen AI untuk menganalisis data struk belanja secara naratif menggunakan local Ollama.
"""
import os
import requests
from dotenv import load_dotenv

from src.config import get_ollama_config
from src.wol import ensure_ryzen_awake

load_dotenv()

_SYSTEM_MSG = """
You are a sharp, pragmatic financial assistant. 
Analyze the user's receipt and summarize it in ONE or TWO natural paragraphs.

RULES FOR YOUR STYLE:
1. **NO HEADERS** (Do not use "Context:", "Tip:", etc.).
2. **NO ROBOTIC FLUFF** (Do not say "Dining out is a great way to unwind").
3. **NO JUDGMENT** (Don't say "Good job" or "Bad job").

HOW TO ANALYZE:
- Weave the context (date/time) naturally into the sentence.
- Mention the total and the merchant clearly.
- If the spending seems high for the category (e.g., $50 for breakfast), point it out objectively.
- If there is a practical tip (like loyalty cards or bulk buying), add it naturally at the end.

Your goal is to sound exactly like a human accountant texting a client. Brief, smart, realistic.
"""


class FinancialCompanion:
    """
    Wrapper class untuk analisis keuangan berbasis LLM menggunakan local Ollama.
    """

    def run_analysis(self, receipt_data) -> str:
        """Menjalankan analisis naratif untuk satu data struk belanja."""
        print("[AI] Financial Companion sedang menganalisis struk menggunakan Ollama...")
        
        cfg = get_ollama_config()
        ensure_ryzen_awake(cfg["api_url"], cfg["ryzen_mac"])

        items_list = ", ".join([
            f"{item.name} ({item.price})"
            for item in receipt_data.items
            if hasattr(item, "name")
        ])

        # Prepare chat payload
        payload = {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": _SYSTEM_MSG},
                {
                    "role": "user",
                    "content": f"Analyze this receipt:\nMerchant: {receipt_data.merchant}\nDate: {receipt_data.date}\nTotal: {receipt_data.total} {receipt_data.currency}\nItems: {items_list}"
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }

        try:
            res = requests.post(f"{cfg['api_url']}/api/chat", json=payload, timeout=60)
            if res.status_code == 200:
                response_data = res.json()
                analysis = response_data.get("message", {}).get("content", "").strip()
                if analysis:
                    return analysis
            print(f"[AI] Ollama returned status code: {res.status_code}")
            return "Failed to analyze receipt details using Ollama."
        except Exception as e:
            print(f"[AI] Error during Ollama analysis query: {e}")
            return f"Error connecting to Ollama analysis engine: {e}"


# ── Singleton instance ────────────────────────────────────────────────────────
_companion = FinancialCompanion()


def run_agent_team(receipt_data) -> str:
    """
    Fungsi helper publik untuk menjalankan analisis AI.
    Menggunakan singleton _companion — tidak ada overhead instansiasi per request.
    """
    return _companion.run_analysis(receipt_data)