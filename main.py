import os
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data

def main():
    # 1. Define where your image is
    # Make sure you put a file named 'test_receipt.jpg' inside the 'data' folder!
    image_name = "test_receipt.jpg"
    image_path = os.path.join("data", image_name)
    
    # 2. Check if file exists before running
    if not os.path.exists(image_path):
        print(f"❌ Error: Please put a receipt image named '{image_name}' in the 'data' folder.")
        return

    # 3. Run the OCR Module
    print("--- Starting OCR Process ---")
    extracted_text = extract_text_from_receipt(image_path)

    """
    # 4. Output the result
    print("\n" + "="*30)
    print("     RAW TEXT RESULT     ")
    print("="*30)
    print(extracted_text)
    print("="*30)
    """

    print(f"✅ OCR Complete ({len(extracted_text)} chars found)")
    print("--- 2. Sending to DeepSeek for Structuring ---")
    receipt_data = extract_structured_data(extracted_text)
    if receipt_data:
        print("\n" + "="*40)
        print("🧾  FINAL PROCESSED RECEIPT")
        print("="*40)
        print(f"🏪 Merchant:  {receipt_data.merchant}")
        print(f"📅 Date:      {receipt_data.date}")
        print(f"💵 Total:     {receipt_data.total} {receipt_data.currency}")
        print(f"🏷️  Category:  {receipt_data.category}")
        print(f"🛒 Items:     {len(receipt_data.items)} found")
        
        print("\nItem Details:")
        for item in receipt_data.items:
            # Handle cases where price might be None
            price = f"{item.price:.2f}" if item.price else "N/A"
            print(f"  - {item.name:<20} {price}")
        print("="*40)
    else:
        print("❌ DeepSeek failed to structure the data.")


if __name__ == "__main__":
    main()