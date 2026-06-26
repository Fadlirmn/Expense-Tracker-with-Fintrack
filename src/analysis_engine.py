"""
analysis_engine.py — Agen AI untuk menganalisis data struk belanja secara naratif.

FIX INEFF-01: FinancialCompanion diinstansiasi sekali sebagai singleton module-level,
bukan dibuat ulang setiap kali run_agent_team() dipanggil.
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# ── Prompt Template (dibuat sekali) ──────────────────────────────────────────
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

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_MSG),
    ("human", """
    Analyze this receipt:
    Merchant: {merchant}
    Date: {date}
    Total: {total}
    Items: {items}
    """)
])

# ── FIX INEFF-01: Singleton LLM dan chain ────────────────────────────────────
_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY"),
)

_chain = _PROMPT | _llm | StrOutputParser()


class FinancialCompanion:
    """
    Wrapper class untuk analisis keuangan berbasis LLM.
    Menggunakan chain yang sudah di-cache di module level (tidak dibuat ulang tiap request).
    """

    def run_analysis(self, receipt_data) -> str:
        """Menjalankan analisis naratif untuk satu data struk belanja."""
        print("[AI] Financial Companion sedang menganalisis struk...")
        items_list = ", ".join([
            f"{item.name} (${item.price})"
            for item in receipt_data.items
            if hasattr(item, "name")
        ])
        return _chain.invoke({
            "merchant": receipt_data.merchant,
            "date":     receipt_data.date,
            "total":    receipt_data.total,
            "items":    items_list,
        })


# ── Singleton instance ────────────────────────────────────────────────────────
_companion = FinancialCompanion()


def run_agent_team(receipt_data) -> str:
    """
    Fungsi helper publik untuk menjalankan analisis AI.
    Menggunakan singleton _companion — tidak ada overhead instansiasi per request.
    """
    return _companion.run_analysis(receipt_data)