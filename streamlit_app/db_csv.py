# streamlit_app/db_csv.py
# ============================================================
# CSV-based data loader for Streamlit Cloud deployment
# Falls back to CSV exports when MySQL is unavailable
# ============================================================

import pandas as pd
import os
import streamlit as st

# Works both locally and on Streamlit Cloud
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "data", "exports")

@st.cache_data
def load_csv(filename):
    path = os.path.join(EXPORT_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    st.error(f"File not found: {filename}")
    return pd.DataFrame()