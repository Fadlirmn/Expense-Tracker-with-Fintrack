"""
fintrack_client.py — HTTP client untuk berkomunikasi dengan FinTrack REST API.

FIX BUG-02: Variabel env kini dibaca di dalam fungsi (lazy), bukan saat module di-import.
Ini mencegah masalah jika load_dotenv() belum dijalankan sebelum modul ini diimpor.
"""
import os
import requests


def _get_base_url() -> str:
    """Mengembalikan base URL FinTrack API dari env (dibaca fresh tiap panggilan)."""
    return os.getenv("FINTRACK_API_URL", "")


def _get_api_key() -> str:
    """Mengembalikan API key FinTrack dari env (dibaca fresh tiap panggilan)."""
    return os.getenv("FINTRACK_API_KEY", "")


def _get_headers() -> dict:
    return {
        "X-API-Key": _get_api_key(),
        "Content-Type": "application/json",
    }


def _is_configured() -> bool:
    """Cek apakah konfigurasi FinTrack sudah lengkap."""
    return bool(_get_base_url() and _get_api_key())


def get_user_id_by_chat_id(chat_id):
    """
    Mencari user_id FinTrack berdasarkan chat_id Telegram.
    Mengembalikan (user_id, error_message).
    """
    if not _is_configured():
        return None, "Konfigurasi FinTrack tidak lengkap (URL/API Key kosong)."

    try:
        url = f"{_get_base_url().rstrip('/')}/internal/v1/binding?chat_id={chat_id}"
        response = requests.get(url, headers=_get_headers(), timeout=10)

        if response.status_code == 404:
            return None, "Akun Telegram Anda belum terhubung dengan akun FinTrack."
        elif response.status_code != 200:
            return None, f"Gagal mengecek binding (HTTP {response.status_code})"

        binding_data = response.json()
        if binding_data.get("linked") and binding_data.get("user_id"):
            return binding_data["user_id"], None
        return None, "Akun Telegram belum terhubung."
    except requests.exceptions.Timeout:
        return None, "Timeout koneksi ke FinTrack API (>10 detik)."
    except Exception as e:
        return None, f"Error koneksi ke FinTrack: {str(e)}"


def create_transaction(user_id: str, category: str, amount: float, description: str):
    """
    Mengirimkan transaksi pengeluaran baru ke FinTrack.
    Mengembalikan (success_boolean, error_message).
    """
    if not _is_configured():
        return False, "Konfigurasi FinTrack tidak lengkap (URL/API Key kosong)."
    if not user_id:
        return False, "User ID tidak boleh kosong."

    try:
        url = f"{_get_base_url().rstrip('/')}/internal/v1/transactions"
        payload = {
            "user_id": user_id,
            "category": category,
            "amount": int(round(amount)),
            "description": description,
        }
        response = requests.post(url, headers=_get_headers(), json=payload, timeout=10)
        if response.status_code == 201:
            return True, "Sukses"
        err_msg = response.json().get("error", "Unknown error")
        return False, f"HTTP {response.status_code}: {err_msg}"
    except requests.exceptions.Timeout:
        return False, "Timeout koneksi ke FinTrack API (>10 detik)."
    except Exception as e:
        return False, str(e)
