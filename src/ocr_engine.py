"""
ocr_engine.py — Engine OCR berbasis Tesseract + OpenCV untuk memproses gambar struk.

FIX BUG-03: File debug processed_receipt.jpg hanya ditulis jika DEBUG=true di env.
IMPROVE OCR: Resize ke min 1200px, sharpen, strip watermark area bawah foto kamera.
"""
import os
import sys
import cv2
import numpy as np
import pytesseract
from src.config import DEBUG

# ── Konfigurasi Platform ───────────────────────────────────────────────────────
if sys.platform.startswith("win"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Tinggi minimum gambar agar Tesseract bisa baca teks kecil dengan baik
MIN_HEIGHT_PX = 1200

# Persentase area bawah yang di-crop untuk hilangkan watermark kamera (HUAWEI, dll)
# 0.07 = 7% dari bawah
WATERMARK_CROP_RATIO = 0.07


def preprocess_image(image_path: str):
    """
    Memuat dan mempersiapkan gambar untuk OCR:
    1. Crop watermark kamera di bagian bawah (HUAWEI NOVA7 AI QUAD CAMERA, dll)
    2. Resize ke minimal MIN_HEIGHT_PX agar teks kecil terbaca
    3. Konversi ke grayscale
    4. Sharpen untuk kontras teks lebih tajam
    5. Thresholding OTSU

    FIX BUG-03: File debug hanya disimpan jika environment DEBUG=true.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Tidak dapat membaca gambar dari path: {image_path}")

    h, w = img.shape[:2]

    # 1. Crop watermark kamera di area bawah gambar
    crop_h = int(h * (1 - WATERMARK_CROP_RATIO))
    img = img[:crop_h, :]

    # 2. Resize jika terlalu kecil — Tesseract butuh resolusi cukup
    if img.shape[0] < MIN_HEIGHT_PX:
        scale = MIN_HEIGHT_PX / img.shape[0]
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 4. Sharpen — perjelas tepi teks
    kernel_sharpen = np.array([[0, -1, 0],
                                [-1, 5, -1],
                                [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel_sharpen)

    # 5. Denoise ringan
    gray = cv2.medianBlur(gray, 3)

    # 6. OTSU thresholding
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
    Mencoba beberapa PSM mode dan mengembalikan hasil terpanjang.

    Args:
        image_path: Path absolut atau relatif ke file gambar struk

    Returns:
        str: Teks yang diekstrak dari gambar
    """
    print(f"[OCR] Scanning: {image_path}...")
    processed_img = preprocess_image(image_path)

    # Coba beberapa PSM mode, ambil hasil terpanjang
    # PSM 6: blok teks seragam (struk ideal)
    # PSM 4: satu kolom teks (struk panjang)
    # PSM 3: auto (fallback)
    best_text = ""
    for psm in [6, 4, 3]:
        try:
            config = f"--psm {psm} --oem 1 -l ind+eng"
            text = pytesseract.image_to_string(processed_img, config=config)
            text = text.strip()
            if len(text) > len(best_text):
                best_text = text
        except Exception:
            continue

    return best_text


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