import os
from dotenv import load_dotenv
from src.analysis_engine import run_agent_team
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data

load_dotenv()


def main():
    image_path = os.path.join("data", "test_receipt.jpg")
    
    if not os.path.exists(image_path):
        print("❌ Image not found.")
        return

    # --- Phase 1: OCR ---
    print("--- 1. OCR Scanning ---")
    raw_text = extract_text_from_receipt(image_path)
    if not raw_text: return

    # --- Phase 2: Structure ---
    print("--- 2. Structuring Data (Groq) ---")
    receipt_data = extract_structured_data(raw_text)
    if not receipt_data: return

    # --- Phase 3: Supportive Analysis ---
    print("\n--- 3. Financial Insight ---")
    
    # Note: We now pass the 'receipt_data' object directly
    final_report = run_agent_team(receipt_data)

    print("\n" + "="*50)
    print("     📊 SMART RECEIPT INSIGHT")
    print("="*50)
    print(final_report)
    print("="*50)
    
if __name__ == "__main__":
    main()