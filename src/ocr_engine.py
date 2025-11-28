import cv2
import pytesseract

# --- CONFIGURATION (WINDOWS ONLY) ---
# If you are on Windows, you must tell Python where Tesseract is installed.
# If you are on Mac/Linux, DELETE this line.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """
    Loads an image and prepares it for OCR by converting to grayscale
    and increasing contrast (thresholding).
    """
    # 1. Load the image using OpenCV
    img = cv2.imread(image_path)
    
    # 2. Convert to Grayscale (removes color noise)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Apply Thresholding (turns grey pixels white, dark pixels black)
    # This creates a sharp black-and-white image which is easier to read.
    # We use 'OTSU' thresholding which automatically finds the best separation point.
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save the processed image just so we can see what the computer sees (Optional)
    cv2.imwrite("processed_receipt.jpg", thresh)
    
    return thresh

def extract_text_from_receipt(image_path):
    """
    Takes an image path and returns the raw string of text found.
    """
    print(f"Scanning: {image_path}...")
    
    # 1. Pre-process the image
    processed_img = preprocess_image(image_path)
    
    # 2. Run Tesseract OCR
    # config='--psm 6' tells Tesseract to assume a single uniform block of text
    text = pytesseract.image_to_string(processed_img, config='--psm 6')
    
    return text

# --- EXECUTION ---
if __name__ == "__main__":
    # Replace 'receipt.jpg' with the actual filename of a receipt on your computer
    image_file = "receipt.jpg" 
    
    try:
        raw_text = extract_text_from_receipt(image_file)
        print("\n--- EXTRACTED TEXT ---")
        print(raw_text)
        print("----------------------")
    except Exception as e:
        print(f"Error: {e}")