import os
from flask import Flask, request, jsonify
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data
from src.analysis_engine import run_agent_team
from dotenv import load_dotenv

# Muat environment variables
load_dotenv()

app = Flask(__name__)
TEMP_DIR = os.path.join("data", "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/scan", methods=["POST"])
def scan_receipt():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No filename"}), 400

    # Save to temporary path
    file_path = os.path.join(TEMP_DIR, uploaded_file.filename)
    try:
        uploaded_file.save(file_path)

        # 1. OCR
        raw_text = extract_text_from_receipt(file_path)
        if not raw_text or not raw_text.strip():
            return jsonify({"error": "Failed to extract text from receipt"}), 422

        # 2. Structured Extraction
        structured_data = extract_structured_data(raw_text)
        if not structured_data:
            return jsonify({"error": "Failed to structure receipt data"}), 422

        # 3. AI Analysis
        ai_analysis = run_agent_team(structured_data)

        # Build response
        items_list = []
        for item in structured_data.items:
            items_list.append({
                "name": item.name,
                "price": item.price
            })

        response_data = {
            "merchant": structured_data.merchant,
            "date": structured_data.date,
            "total": structured_data.total,
            "currency": structured_data.currency,
            "category": structured_data.category,
            "items": items_list,
            "analysis": ai_analysis
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"❌ Error during API scan: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Failed to remove temp file: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"⚡ Expense Tracker API Server is starting on port {port}...")
    app.run(host="0.0.0.0", port=port)
