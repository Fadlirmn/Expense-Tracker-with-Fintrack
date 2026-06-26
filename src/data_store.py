"""
data_store.py — Modul tunggal untuk operasi baca/tulis data pengeluaran ke JSON.
Menggantikan fungsi save_expense() yang terduplikasi di bot.py dan app.py.
"""
import json
import os
from datetime import datetime
from src.config import DATA_FILE


def load_expenses() -> list:
    """Memuat seluruh riwayat pengeluaran dari berkas JSON. Mengembalikan list kosong jika belum ada."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_expense(receipt_data, analysis_text: str) -> None:
    """
    Menyimpan satu entri pengeluaran terstruktur ke berkas log JSON.
    
    Args:
        receipt_data: Objek ReceiptData (Pydantic) atau dict
        analysis_text: Teks analisis AI dari FinancialCompanion
    """
    # Support both Pydantic model and plain dict
    if hasattr(receipt_data, "dict"):
        new_entry = receipt_data.dict()
    elif hasattr(receipt_data, "model_dump"):
        new_entry = receipt_data.model_dump()
    else:
        new_entry = dict(receipt_data)

    new_entry["ai_analysis"] = analysis_text
    new_entry["scanned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    history = load_expenses()
    history.append(new_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
