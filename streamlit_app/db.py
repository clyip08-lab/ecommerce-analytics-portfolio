# streamlit_app/db.py
# ============================================================
# Data loader — CSV-based for Streamlit Cloud deployment
# ============================================================

import pandas as pd
import os
import streamlit as st

# Works on both local and Streamlit Cloud
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "data", "exports")

@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV export file directly."""
    path = os.path.join(EXPORT_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path, dtype={"cohort_month": str})
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        return df
    st.warning(f"⚠️ File not found: {filename}")
    return pd.DataFrame()

@st.cache_data
def run_query(query: str) -> pd.DataFrame:
    """
    Map SQL view names → pre-exported CSV files.
    No MySQL connection needed.
    """
    q = query.lower()

    if "vw_monthly_revenue"    in q: return load_csv("analysis_monthly.csv")
    if "vw_conversion_funnel"  in q: return load_csv("analysis_funnel.csv")
    if "vw_brand_performance"  in q: return load_csv("analysis_brands.csv")
    if "vw_product_performance"in q: return load_csv("analysis_categories.csv")
    if "vw_daily_kpis"         in q: return load_csv("analysis_daily.csv")
    if "vw_user_retention"     in q: return load_csv("analysis_rfm_segments.csv")
    if "dim_sessions"          in q: return load_csv("dim_sessions.csv")
    if "dim_products"          in q: return load_csv("dim_products.csv")

    # Inline queries (hourly, funnel counts etc) → use fact_events CSV
    if "fact_events"           in q: return load_csv("fact_events.csv")

    st.warning(f"⚠️ No CSV mapped for this query.")
    return pd.DataFrame()