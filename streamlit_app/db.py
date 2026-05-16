# streamlit_app/db.py
# ============================================================
# Database connection — shared across all pages
# ============================================================

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ecommerce_analytics")

@st.cache_resource
def get_engine():
    """Create DB engine — cached so it's only created once."""
    conn_str = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(conn_str, echo=False)

@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    """Run SQL query → return DataFrame. Cached for 10 minutes."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows   = result.fetchall()
        cols   = result.keys()
        df     = pd.DataFrame(rows, columns=cols)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        return df