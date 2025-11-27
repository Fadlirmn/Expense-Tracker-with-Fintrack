import os
from src.ocr_engine import extract_text_from_receipt

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
    
    # 4. Output the result
    print("\n" + "="*30)
    print("     RAW TEXT RESULT     ")
    print("="*30)
    print(extracted_text)
    print("="*30)

if __name__ == "__main__":
    main()