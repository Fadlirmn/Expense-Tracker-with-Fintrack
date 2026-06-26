import os
import json
import telebot
from datetime import datetime
from dotenv import load_dotenv

# Import module pipeline
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data
from src.analysis_engine import run_agent_team
from src.fintrack_client import get_user_id_by_chat_id, create_transaction

# Muat environment variables
load_dotenv()

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "")
DATA_FILE = os.getenv("DATA_FILE", os.path.join("data", "expenses_log.json"))
TEMP_DIR = os.path.join("data", "temp_uploads")
FINTRACK_API_URL = os.getenv("FINTRACK_API_URL")
FINTRACK_API_KEY = os.getenv("FINTRACK_API_KEY")

# Pastikan folder ada
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Parse whitelist User ID
allowed_user_ids = []
if ALLOWED_USERS:
    try:
        allowed_user_ids = [int(uid.strip()) for uid in ALLOWED_USERS.split(",") if uid.strip()]
    except ValueError:
        print("❌ Gagal mem-parse ALLOWED_TELEGRAM_USER_IDS. Pastikan formatnya adalah angka dipisahkan koma.")

if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di environment variables. Bot tidak dapat dijalankan.")
    exit(1)

bot = telebot.TeleBot(TOKEN)

def is_allowed(user_id):
    # Jika ALLOWED_TELEGRAM_USER_IDS dikosongkan, izinkan semua (opsi fallback lokal)
    if not allowed_user_ids:
        return True
    return user_id in allowed_user_ids

def save_expense(receipt_data, analysis_text):
    """Menyimpan data pengeluaran terstruktur ke berkas log JSON."""
    new_entry = receipt_data.dict()
    new_entry['ai_analysis'] = analysis_text
    new_entry['scanned_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
            except Exception:
                history = []

    history.append(new_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_allowed(message.from_user.id):
        bot.reply_to(message, "⚠️ Maaf, Anda tidak memiliki izin untuk menggunakan bot ini.")
        return
    
    welcome_text = (
        "🤖 <b>Selamat datang di AI Expense Tracker Bot!</b>\n\n"
        "Kirimkan foto struk belanja Anda di sini. Saya akan:\n"
        "1. Membaca teks pada struk (OCR)\n"
        "2. Mengekstrak merchant, tanggal, total, dan barang (Groq Llama 3)\n"
        "3. Menganalisis pengeluaran Anda (Financial Companion)\n"
        "4. Menyimpannya ke database Dashboard\n\n"
        "<i>Silakan kirim foto struk untuk memulai!</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_receipt_photo(message):
    if not is_allowed(message.from_user.id):
        bot.reply_to(message, "⚠️ Maaf, Anda tidak memiliki izin untuk menggunakan bot ini.")
        return

    # Kirim status awal
    status_msg = bot.reply_to(message, "📸 <b>Foto diterima.</b> Sedang mengunduh berkas...", parse_mode="HTML")

    file_path = None
    try:
        # 1. Unduh berkas foto dengan resolusi tertinggi
        photo_file = message.photo[-1]
        file_info = bot.get_file(photo_file.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Simpan ke folder temporary
        filename = f"{photo_file.file_id}.jpg"
        file_path = os.path.join(TEMP_DIR, filename)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # 2. Proses OCR
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text="⏳ <b>OCR scanning...</b> Sedang mengekstrak teks dari struk.",
            parse_mode="HTML"
        )
        raw_text = extract_text_from_receipt(file_path)

        if not raw_text or not raw_text.strip():
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text="❌ <b>Gagal membaca teks struk.</b> Pastikan foto cukup jelas dan terang.",
                parse_mode="HTML"
            )
            return

        # 3. Ekstraksi Data Terstruktur
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text="🧠 <b>AI Extraction...</b> Mengekstrak informasi penting via Groq Llama 3.",
            parse_mode="HTML"
        )
        structured_data = extract_structured_data(raw_text)

        if not structured_data:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text="❌ <b>Gagal menstrukturkan data.</b> Model LLM gagal mengekstrak data dari teks OCR.",
                parse_mode="HTML"
            )
            return

        # 4. Analisis Keuangan
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text="📊 <b>AI Analysis...</b> Menganalisis pola belanja dengan Financial Companion.",
            parse_mode="HTML"
        )
        ai_analysis = run_agent_team(structured_data)

        # 5. Simpan ke Database JSON
        save_expense(structured_data, ai_analysis)

        # 6. Sinkronisasi ke FinTrack jika terkonfigurasi
        sync_status = ""
        if FINTRACK_API_URL and FINTRACK_API_KEY:
            description = f"Scan Struk: {structured_data.merchant}"
            if structured_data.items:
                items_summary = ", ".join([item.name for item in structured_data.items])
                if len(items_summary) > 60:
                    items_summary = items_summary[:57] + "..."
                description += f" ({items_summary})"

            user_id, err = get_user_id_by_chat_id(message.from_user.id)
            if user_id:
                success, tx_err = create_transaction(
                    user_id=user_id,
                    category=structured_data.category,
                    amount=structured_data.total,
                    description=description
                )
                if success:
                    sync_status = "\n🔗 <b>Tersinkronisasi dengan FinTrack!</b>\n"
                else:
                    sync_status = f"\n⚠️ <b>FinTrack Sync Gagal:</b> <i>{tx_err}</i>\n"
            else:
                sync_status = f"\n⚠️ <b>FinTrack Sync Gagal:</b> <i>{err}</i>\n"

        # 7. Format Laporan untuk Pengguna
        items_list = ""
        for item in structured_data.items:
            price_str = f"${item.price:,.2f}" if item.price is not None else "N/A"
            items_list += f"  • {item.name} ({price_str})\n"
        if not items_list:
            items_list = "  • (Tidak ada detail item)\n"

        currency_symbol = structured_data.currency
        report_html = (
            "📊 <b>SMART RECEIPT INSIGHT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏪 <b>Merchant:</b> {structured_data.merchant}\n"
            f"📅 <b>Date:</b> {structured_data.date}\n"
            f"💰 <b>Total:</b> {currency_symbol} {structured_data.total:,.2f}\n"
            f"📂 <b>Category:</b> {structured_data.category}\n\n"
            f"🛒 <b>Items:</b>\n{items_list}\n"
            f"💬 <b>AI Analysis:</b>\n{ai_analysis}\n"
            f"{sync_status}\n"
            "✅ <i>Struk berhasil diproses dan disimpan ke Dashboard!</i>"
        )

        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        bot.reply_to(message, report_html, parse_mode="HTML")

    except Exception as e:
        print(f"❌ Error handling photo: {e}")
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"🚨 <b>Terjadi kesalahan sistem:</b> <code>{str(e)}</code>",
            parse_mode="HTML"
        )
    finally:
        # Cleanup file temporary
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Gagal menghapus file temp {file_path}: {e}")

if __name__ == "__main__":
    print("⚡ AI Expense Tracker Bot is running...")
    bot.infinity_polling()
