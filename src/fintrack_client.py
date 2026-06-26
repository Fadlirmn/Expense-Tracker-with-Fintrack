import os
import requests

# Muat environment variables jika belum (dotenv diimpor di pemanggil)
FINTRACK_API_URL = os.getenv("FINTRACK_API_URL")
FINTRACK_API_KEY = os.getenv("FINTRACK_API_KEY")

def get_headers():
    return {
        "X-API-Key": FINTRACK_API_KEY,
        "Content-Type": "application/json"
    }

def get_user_id_by_chat_id(chat_id):
    """
    Mencari user_id FinTrack berdasarkan chat_id Telegram.
    Mengembalikan (user_id, error_message).
    """
    if not FINTRACK_API_URL or not FINTRACK_API_KEY:
        return None, "Konfigurasi FinTrack tidak lengkap (URL/API Key kosong)."

    try:
        url = f"{FINTRACK_API_URL.rstrip('/')}/internal/v1/binding?chat_id={chat_id}"
        response = requests.get(url, headers=get_headers(), timeout=10)

        if response.status_code == 404:
            return None, "Akun Telegram Anda belum terhubung dengan akun FinTrack."
        elif response.status_code != 200:
            return None, f"Gagal mengecek binding (HTTP {response.status_code})"

        binding_data = response.json()
        if binding_data.get("linked") and binding_data.get("user_id"):
            return binding_data["user_id"], None
        return None, "Akun Telegram belum terhubung."
    except Exception as e:
        return None, f"Error koneksi ke FinTrack: {str(e)}"

def create_transaction(user_id, category, amount, description):
    """
    Mengirimkan transaksi pengeluaran baru ke FinTrack.
    Mengembalikan (success_boolean, error_message).
    """
    if not FINTRACK_API_URL or not FINTRACK_API_KEY or not user_id:
        return False, "Konfigurasi FinTrack tidak lengkap (URL/API Key/User ID kosong)."

    try:
        url = f"{FINTRACK_API_URL.rstrip('/')}/internal/v1/transactions"
        payload = {
            "user_id": user_id,
            "category": category,
            "amount": int(round(amount)),
            "description": description
        }

        response = requests.post(url, headers=get_headers(), json=payload, timeout=10)
        if response.status_code == 201:
            return True, "Sukses"
        else:
            err_msg = response.json().get("error", "Unknown error")
            return False, f"HTTP {response.status_code}: {err_msg}"
    except Exception as e:
        return False, str(e)
