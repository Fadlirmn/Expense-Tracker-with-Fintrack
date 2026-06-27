"""
config.py — Sumber kebenaran tunggal untuk konfigurasi dan helper bersama.
Semua modul lain harus mengimpor konstanta dari sini, bukan mendefinisikan ulang.
"""
import os
from dotenv import load_dotenv

# Muat environment variables (aman dipanggil berkali-kali)
load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_FILE = os.getenv("DATA_FILE", os.path.join("data", "expenses_log.json"))
TEMP_DIR  = os.path.join("data", "temp_uploads")
DEBUG     = os.getenv("DEBUG", "false").lower() == "true"

# ── FinTrack Integration ───────────────────────────────────────────────────────
# Dibaca sebagai fungsi agar selalu up-to-date dan aman terhadap urutan import.
def get_fintrack_config():
    """Mengembalikan (FINTRACK_API_URL, GATEWAY_API_KEY) yang selalu fresh dari env."""
    return os.getenv("FINTRACK_API_URL"), os.getenv("GATEWAY_API_KEY")

# ── Ollama & Ryzen Integration ────────────────────────────────────────────────
def get_ollama_config():
    """Mengembalikan konfigurasi Ollama dan Ryzen."""
    return {
        "api_url": os.getenv("OLLAMA_API_URL", "http://localhost:11435"),
        "model": os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        "ryzen_ip": os.getenv("RYZEN_IP", "192.168.100.22"),
        "ryzen_mac": os.getenv("RYZEN_MAC", "9c:6b:00:07:66:cd")
    }

# ── Upload Constraints ─────────────────────────────────────────────────────────
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB limit untuk upload gambar struk

# ── Shared Description Builder ─────────────────────────────────────────────────
def build_description(merchant: str, items, prefix: str = "Scan Struk") -> str:
    """
    Membangun string deskripsi transaksi yang konsisten dari merchant dan items.
    Digunakan oleh api.py, app.py, dan bot.py untuk menghindari duplikasi logika.
    
    Args:
        merchant: Nama toko/merchant
        items: List item (harus memiliki atribut .name atau key 'name')
        prefix: Awalan deskripsi (default: 'Scan Struk')
    
    Returns:
        str: Deskripsi terformat, max ~75 karakter
    """
    description = f"{prefix}: {merchant}"
    if items:
        # Support both Pydantic objects (.name) and dicts ('name')
        names = []
        for item in items:
            if hasattr(item, "name"):
                names.append(item.name)
            elif isinstance(item, dict):
                names.append(item.get("name", ""))
        if names:
            items_summary = ", ".join(names)
            if len(items_summary) > 60:
                items_summary = items_summary[:57] + "..."
            description += f" ({items_summary})"
    return description
