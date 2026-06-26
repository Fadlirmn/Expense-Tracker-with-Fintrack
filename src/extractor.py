"""
extractor.py — Ekstraksi data terstruktur dari teks OCR menggunakan Groq Llama 3.

FIX INEFF-02: Objek prompt dan chain kini dibuat sekali di module level (bukan per panggilan).
Ini mengurangi overhead instansiasi yang tidak perlu pada setiap request scan.
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


# ── Schema ────────────────────────────────────────────────────────────────────

class ReceiptItem(BaseModel):
    name:  str            = Field(description="Name of the item purchased")
    price: Optional[float] = Field(description="Price of the individual item")


class ReceiptData(BaseModel):
    merchant: str                    = Field(description="Name of the store or merchant", default="Unknown")
    date:     Optional[str]          = Field(description="Date of transaction in YYYY-MM-DD format. Use 'Unknown' if not found.", default="Unknown")
    total:    Optional[float]        = Field(description="The final total amount paid. Use 0 if not found.", default=0.0)
    currency: Optional[str]          = Field(description="Currency code (IDR, USD, EUR, etc.). Use 'IDR' if not found.", default="IDR")
    category: Optional[str]          = Field(description="Category: Groceries, Transport, Dining, Electronics, Utilities, or Other.", default="Other")
    items:    List[ReceiptItem]      = Field(description="List of line items", default_factory=list)


# ── FIX INEFF-02: LLM, parser, prompt, dan chain dibuat sekali di module level ──

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0,
    api_key=os.getenv("GROQ_API_KEY"),
)

_parser = PydanticOutputParser(pydantic_object=ReceiptData)

_prompt = PromptTemplate(
    template="""
You are an expert receipt/invoice data extractor. Extract structured data from this OCR text.

OCR TEXT:
{text}

INSTRUCTIONS:
1. Fix common OCR errors (e.g., 'S' vs '5', 'O' vs '0', 'l' vs '1').
2. Extract all available fields. For missing fields, use these defaults:
   - date: "Unknown"
   - total: 0
   - currency: "IDR"
   - category: "Other"
   - merchant: "Unknown"
3. If the text does NOT look like a receipt (e.g., it's a photo watermark, random text, or camera info), still return valid JSON with all defaults.
4. Return ONLY valid JSON, no explanation.

{format_instructions}
""",
    input_variables=["text"],
    partial_variables={"format_instructions": _parser.get_format_instructions()},
)

# Chain di-cache: tidak dibuat ulang per request
_chain = _prompt | _llm | _parser


# ── Extraction Function ───────────────────────────────────────────────────────

def extract_structured_data(raw_ocr_text: str) -> Optional[ReceiptData]:
    """
    Mengirimkan teks OCR ke Groq Llama 3 dan mengekstrak data terstruktur.
    
    Args:
        raw_ocr_text: Teks mentah hasil OCR Tesseract
        
    Returns:
        ReceiptData atau None jika gagal
    """
    print(f"[Extractor] Mengirim {len(raw_ocr_text)} karakter ke Groq Llama 3...")
    try:
        result = _chain.invoke({"text": raw_ocr_text})
        return result
    except Exception as e:
        print(f"[Extractor] Extraction Error: {e}")
        return None