# Project Context: Expense Tracker Agent

## Project Overview

This project is an intelligent expense tracker that processes images of receipts. It uses Optical Character Recognition (OCR) to digitize the receipt, then leverages Large Language Models (LLMs) via the Groq API to extract structured data and provide financial analysis. The entire application is wrapped in a user-friendly web interface created with Streamlit.

The core pipeline is as follows:

1.  **Image Upload**: The user uploads a receipt image via the Streamlit web UI.
2.  **OCR Processing**: The image is pre-processed (grayscale, thresholding) with OpenCV and then scanned by Tesseract OCR to extract raw text.
3.  **Structured Data Extraction**: The raw text is sent to a Groq Llama 3 model, which is prompted to return a clean JSON object containing the merchant, date, total, currency, category, and line items.
4.  **Financial Analysis**: The structured data is then passed to a second LLM agent (also Groq Llama 3) which analyzes the spending and provides a concise, human-like summary and tip.
5.  **Logging**: The extracted data is appended to `expenses_log.json` for persistent storage.

## Key Technologies

- **Frontend**: Streamlit
- **Backend/Orchestration**: Python
- **OCR**: Tesseract, OpenCV (`opencv-python`)
- **LLM Integration**: Groq API, LangChain (`langchain-groq`)
- **Data Manipulation**: Pandas

## Building and Running

### 1. Prerequisites

- Python 3.10+
- Tesseract OCR Engine:
  - **Windows**: Download and run the installer from the [official Tesseract repository](https://github.com/UB-Mannheim/tesseract/wiki). **Important**: Ensure you add Tesseract to your system's PATH. The `src/ocr_engine.py` file may contain a hardcoded path that might need adjustment for your system (`C:\Program Files\Tesseract-OCR\tesseract.exe`).
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`

### 2. Setup API Keys

1.  Create a file named `.env` in the root of the project directory.
2.  Add your Groq API key to this file:
    ```
    GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxx"
    ```

### 3. Installation

It is highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

### 4. Running the Application

Once the setup is complete, run the Streamlit application from the terminal:

```bash
streamlit run main.py
```

This will start the web server and open the application in your default web browser.

## Development Conventions

- **Configuration**: All secret keys, like the Groq API key, are managed via a `.env` file and loaded using `python-dotenv`.
- **Modularity**: The project is organized into distinct modules within the `src/` directory, separating concerns:
  - `ocr_engine.py`: Handles all image processing and text recognition.
  - `extractor.py`: Handles communication with the LLM for data parsing.
  - `analysis_engine.py`: Contains the logic for the financial analysis agent.
- **Entry Point**: The main application logic and UI are in `main.py`. The `app.py` file is a simple wrapper.
- **Data Storage**: Processed expenses are stored in `expenses_log.json`, a simple and portable format.
- **LLM Prompting**: Prompts are clearly defined within the functions that call the LLM. The extractor uses a `PydanticOutputParser` to ensure the LLM returns a specific JSON schema. The analysis agent is styled to be "sharp, pragmatic" and avoid robotic fluff.
