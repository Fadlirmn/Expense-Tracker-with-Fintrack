"""
extractor.py — Ekstraksi data terstruktur dari teks OCR menggunakan local Ollama (Llama 3.1).
"""
import os
import json
import requests
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

from src.config import get_ollama_config
from src.wol import ensure_ryzen_awake

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


# ── Extraction Function ───────────────────────────────────────────────────────

def extract_structured_data(raw_ocr_text: str) -> Optional[ReceiptData]:
    """
    Mengirimkan teks OCR ke local Ollama dan mengekstrak data terstruktur.
    
    Args:
        raw_ocr_text: Teks mentah hasil OCR Tesseract
        
    Returns:
        ReceiptData atau None jika gagal
    """
    cfg = get_ollama_config()
    print(f"[Extractor] Memastikan Ryzen node bangun di {cfg['api_url']}...")
    ensure_ryzen_awake(cfg["api_url"], cfg["ryzen_mac"])

    prompt = f"""You are an expert receipt/invoice data extractor. Extract structured data from this OCR text.

OCR TEXT:
{raw_ocr_text}

INSTRUCTIONS:
1. Fix common OCR errors (e.g., 'S' vs '5', 'O' vs '0', 'l' vs '1').
2. Extract all available fields.
3. Return ONLY a valid JSON object matching this schema:
{{
  "merchant": "Name of the store or merchant (default: 'Unknown')",
  "date": "Date of transaction in YYYY-MM-DD format (default: 'Unknown')",
  "total": 0.0 (The final total amount paid as float, default: 0.0),
  "currency": "Currency code like IDR, USD, etc. (default: 'IDR')",
  "category": "Category: Groceries, Transport, Dining, Electronics, Utilities, or Other. (default: 'Other')",
  "items": [
    {{
      "name": "Name of the item purchased",
      "price": 0.0 (Price of the individual item as float)
    }}
  ]
}}
Do not include any markdown styling, explanation or robotic text. Return ONLY the JSON object.
"""

    print(f"[Extractor] Mengirim {len(raw_ocr_text)} karakter ke local Ollama model {cfg['model']}...")
    try:
        payload = {
            "model": cfg["model"],
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        res = requests.post(f"{cfg['api_url']}/api/generate", json=payload, timeout=90)
        if res.status_code != 200:
            print(f"[Extractor] Ollama returned status code: {res.status_code}")
            return None
            
        response_data = res.json()
        response_text = response_data.get("response", "").strip()
        
        # Parse returned JSON
        data_dict = json.loads(response_text)
        
        # Normalize and construct ReceiptData Pydantic object
        items = []
        for item in data_dict.get("items", []):
            if isinstance(item, dict) and "name" in item:
                # Ensure price is float
                price_val = item.get("price")
                try:
                    price_val = float(price_val) if price_val is not None else 0.0
                except (ValueError, TypeError):
                    price_val = 0.0
                items.append(ReceiptItem(name=item["name"], price=price_val))
                
        total_val = data_dict.get("total")
        try:
            total_val = float(total_val) if total_val is not None else 0.0
        except (ValueError, TypeError):
            total_val = 0.0

        receipt_data = ReceiptData(
            merchant=data_dict.get("merchant", "Unknown") or "Unknown",
            date=data_dict.get("date", "Unknown") or "Unknown",
            total=total_val,
            currency=data_dict.get("currency", "IDR") or "IDR",
            category=data_dict.get("category", "Other") or "Other",
            items=items
        )
        return receipt_data

    except Exception as e:
        print(f"[Extractor] Extraction Error: {e}")
        return None