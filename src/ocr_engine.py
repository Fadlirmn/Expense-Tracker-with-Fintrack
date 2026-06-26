"""
ocr_engine.py — Engine OCR berbasis Tesseract + OpenCV untuk memproses gambar struk.

FIX BUG-03: File debug processed_receipt.jpg hanya ditulis jika DEBUG=true di env.
"""
import os
import sys
import cv2
import pytesseract
from src.config import DEBUG

# ── Konfigurasi Platform ───────────────────────────────────────────────────────
if sys.platform.startswith("win"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(image_path: str):
    """
    Memuat gambar dan mempersiapkannya untuk OCR:
    - Konversi ke grayscale (hilangkan noise warna)
    - Thresholding OTSU (kontras tajam untuk Tesseract)
    
    FIX BUG-03: File debug hanya disimpan jika environment DEBUG=true.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Tidak dapat membaca gambar dari path: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Hanya simpan file debug jika DEBUG=true (FIX BUG-03)
    if DEBUG:
        debug_path = os.path.join("processed_debug", "processed_receipt.jpg")
        os.makedirs("processed_debug", exist_ok=True)
        cv2.imwrite(debug_path, thresh)

    return thresh


def extract_text_from_receipt(image_path: str) -> str:
    """
    Menerima path gambar dan mengembalikan teks mentah hasil OCR Tesseract.
    
    Args:
        image_path: Path absolut atau relatif ke file gambar struk
        
    Returns:
        str: Teks yang diekstrak dari gambar
    """
    print(f"[OCR] Scanning: {image_path}...")
    processed_img = preprocess_image(image_path)
    # --psm 6: Asumsikan satu blok teks seragam (cocok untuk struk belanja)
    text = pytesseract.image_to_string(processed_img, config="--psm 6")
    return text


# ── Standalone Execution ───────────────────────────────────────────────────────
if __name__ == "__main__":
    image_file = sys.argv[1] if len(sys.argv) > 1 else "receipt.jpg"
    try:
        raw_text = extract_text_from_receipt(image_file)
        print("\n--- EXTRACTED TEXT ---")
        print(raw_text)
        print("----------------------")
    except Exception as e:
        print(f"Error: {e}")