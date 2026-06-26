import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Import modules — gunakan shared modules (FIX REDUN-02, 03, 04)
from src.config import DATA_FILE, TEMP_DIR, build_description
from src.data_store import save_expense, load_expenses
from src.ocr_engine import extract_text_from_receipt
from src.extractor import extract_structured_data
from src.analysis_engine import run_agent_team
from src.fintrack_client import create_transaction

load_dotenv()

# Konfigurasi FinTrack (dibaca fresh, bukan di module level)
DEFAULT_FINTRACK_USER_ID = os.getenv("DEFAULT_FINTRACK_USER_ID")

# Pastikan direktori temp ada
os.makedirs(TEMP_DIR, exist_ok=True)

st.set_page_config(page_title="AI Expense Tracker", page_icon="💰", layout="wide")



def save_and_sync(receipt_data, analysis_text: str) -> None:
    """Simpan struk ke JSON lokal dan sinkronisasi ke FinTrack jika dikonfigurasi."""
    # Gunakan shared save_expense dari data_store (FIX REDUN-02)
    save_expense(receipt_data, analysis_text)

    # Sync ke FinTrack jika DEFAULT_FINTRACK_USER_ID tersedia
    if DEFAULT_FINTRACK_USER_ID:
        # Gunakan shared build_description (FIX REDUN-01)
        description = build_description(receipt_data.merchant, receipt_data.items, prefix="Scan Struk (Web)")
        success, err = create_transaction(
            user_id=DEFAULT_FINTRACK_USER_ID,
            category=receipt_data.category,
            amount=receipt_data.total,
            description=description,
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
    # Gunakan load_expenses dari data_store (FIX REDUN-02)
    import pandas as pd
    raw_data = load_expenses()
    df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

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

                            # D. Save & Sync (FIX REDUN-02: gunakan save_and_sync)
                            save_and_sync(structured_data, ai_analysis)

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