import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime

# Import your existing modules
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data
from src.analysis_engine import run_agent_team
from src.fintrack_client import create_transaction

# --- CONFIGURATION ---
DATA_FILE = os.getenv("DATA_FILE", os.path.join("data", "expenses_log.json"))
TEMP_DIR = os.path.join("data", "temp_uploads")
FINTRACK_API_URL = os.getenv("FINTRACK_API_URL")
FINTRACK_API_KEY = os.getenv("FINTRACK_API_KEY")
DEFAULT_FINTRACK_USER_ID = os.getenv("DEFAULT_FINTRACK_USER_ID")

# Ensure temp directory exists
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

st.set_page_config(page_title="AI Expense Tracker", page_icon="💰", layout="wide")

# --- HELPER FUNCTIONS ---
def load_data():
    """Loads the JSON database into a Pandas DataFrame."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except json.JSONDecodeError:
        return pd.DataFrame()

def save_expense(receipt_data, analysis_text):
    """Saves a processed receipt to the JSON file."""
    new_entry = receipt_data.dict()
    new_entry['ai_analysis'] = analysis_text
    new_entry['scanned_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load existing
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []
    else:
        history = []

    history.append(new_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

    # Sync to FinTrack if configured
    if FINTRACK_API_URL and FINTRACK_API_KEY and DEFAULT_FINTRACK_USER_ID:
        description = f"Scan Struk (Web): {receipt_data.merchant}"
        if receipt_data.items:
            items_summary = ", ".join([item.name for item in receipt_data.items])
            if len(items_summary) > 60:
                items_summary = items_summary[:57] + "..."
            description += f" ({items_summary})"

        success, err = create_transaction(
            user_id=DEFAULT_FINTRACK_USER_ID,
            category=receipt_data.category,
            amount=receipt_data.total,
            description=description
        )
        if success:
            print("✅ Sinkronisasi FinTrack dari Web berhasil.")
        else:
            print(f"⚠️ Gagal sinkronisasi FinTrack dari Web: {err}")

# --- UI LAYOUT ---
st.title("💰 AI Expense Tracker Agent")

# Create Tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "📸 Scan Receipts"])

# ==========================
# TAB 1: DASHBOARD
# ==========================
with tab1:
    df = load_data()

    if df.empty:
        st.info("No expenses logged yet. Go to the 'Scan Receipts' tab to get started!")
    else:
        # Convert date column to datetime objects for sorting
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 1. TOP METRICS
        col1, col2, col3 = st.columns(3)
        total_spent = df['total'].sum()
        transaction_count = len(df)
        latest_merchant = df.iloc[-1]['merchant'] if not df.empty else "N/A"

        col1.metric("Total Spent", f"${total_spent:,.2f}")
        col2.metric("Transactions", transaction_count)
        col3.metric("Last Visit", latest_merchant)

        st.divider()

        # 2. CHARTS
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Spending by Category")
            # Group by Category
            category_spend = df.groupby("category")['total'].sum()
            st.bar_chart(category_spend)

        with col_chart2:
            st.subheader("Recent Activity")
            # Show a clean table of recent transactions
            st.dataframe(
                df[['date', 'merchant', 'category', 'total']].sort_values(by='date', ascending=False),
                hide_index=True,
                use_container_width=True
            )

# ==========================
# TAB 2: SCANNER
# ==========================
with tab2:
    st.write("Upload one or multiple receipt images. The Agent will process them sequentially.")
    
    uploaded_files = st.file_uploader("Choose receipt images...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if st.button("Process Receipts") and uploaded_files:
        
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # 1. Save temp file (OCR needs a file path usually)
            file_path = os.path.join(TEMP_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 2. Display Image
            col_img, col_info = st.columns([1, 2])
            with col_img:
                st.image(uploaded_file, caption=f"Receipt: {uploaded_file.name}", width=250)

            with col_info:
                with st.spinner(f"Agent is analyzing {uploaded_file.name}..."):
                    
                    # --- PIPELINE START ---
                    # A. OCR
                    raw_text = extract_text_from_receipt(file_path)
                    
                    if raw_text:
                        # B. Extraction
                        structured_data = extract_structured_data(raw_text)
                        
                        if structured_data:
                            # C. AI Analysis
                            ai_analysis = run_agent_team(structured_data)
                            
                            # D. Save
                            save_expense(structured_data, ai_analysis)
                            
                            # E. Show Result
                            st.success(f"Processed: {structured_data.merchant} (${structured_data.total})")
                            with st.expander("💬 Read Agent's Insight", expanded=True):
                                st.write(ai_analysis)
                        else:
                            st.error("AI extraction failed. Could not structure data.")
                    else:
                        st.error("OCR failed. No text found.")
                    # --- PIPELINE END ---

            # Cleanup temp file
            os.remove(file_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        st.success("All receipts processed! Check the Dashboard tab to see updated stats.")