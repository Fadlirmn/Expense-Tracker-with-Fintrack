"""
api.py — Flask REST API server untuk endpoint scan struk belanja.
Digunakan oleh FinTrack bot-gateway (Go) untuk mengirimkan gambar struk via multipart form-data.

FIX INEFF-04: Tambahkan limit ukuran upload (10 MB) untuk mencegah memory spike.
FIX REDUN-03/04: Gunakan konstanta dari src.config, bukan redefinisi lokal.
"""
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.config import TEMP_DIR, MAX_UPLOAD_BYTES, build_description
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data
from src.analysis_engine import run_agent_team

# Muat environment variables
load_dotenv()

app = Flask(__name__)

# FIX INEFF-04: Batasi ukuran request maksimum
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

os.makedirs(TEMP_DIR, exist_ok=True)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/scan", methods=["POST"])
def scan_receipt():
    """
    Endpoint utama: menerima gambar struk belanja via multipart form-data,
    menjalankan pipeline OCR → Ekstraksi → Analisis AI, lalu mengembalikan JSON.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"error": "No filename provided"}), 400

    file_path = os.path.join(TEMP_DIR, uploaded_file.filename)
    try:
        uploaded_file.save(file_path)

        # 1. OCR
        raw_text = extract_text_from_receipt(file_path)
        if not raw_text or not raw_text.strip():
            return jsonify({"error": "Failed to extract text from receipt image"}), 422

        # 2. Structured Extraction
        structured_data = extract_structured_data(raw_text)
        if not structured_data:
            return jsonify({"error": "Failed to structure receipt data from OCR text"}), 422

        # 3. AI Analysis
        ai_analysis = run_agent_team(structured_data)

        # 4. Build response — gunakan build_description dari config (FIX REDUN-01)
        items_list = [
            {"name": item.name, "price": item.price}
            for item in structured_data.items
        ]

        return jsonify({
            "merchant":  structured_data.merchant,
            "date":      structured_data.date,
            "total":     structured_data.total,
            "currency":  structured_data.currency,
            "category":  structured_data.category,
            "items":     items_list,
            "analysis":  ai_analysis,
            # Field tambahan: deskripsi siap pakai untuk Go handler
            "description": build_description(structured_data.merchant, structured_data.items),
        }), 200

    except Exception as e:
        print(f"[API] Error during scan: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"[API] Warning: Gagal menghapus file temp {file_path}: {e}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"⚡ Expense Tracker API Server starting on port {port}...")
    app.run(host="0.0.0.0", port=port)
