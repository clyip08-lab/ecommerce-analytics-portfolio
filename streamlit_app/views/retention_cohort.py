
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import load_csv


def show():

    st.title("📈 Cohort Retention Analysis")

    st.markdown("""
    Analyze customer retention by cohort month to understand repeat purchase behavior over time.
    """)

    # ============================================================
    # LOAD DATA
    # ============================================================

    df_cohort = load_csv("analysis_cohort_long.csv")

    if df_cohort.empty:
        st.warning("No cohort data found.")
        return

    # ============================================================
    # CLEAN DATA
    # ============================================================

    # Force cohort month to string
    df_cohort["cohort_month"] = (
        df_cohort["cohort_month"]
        .astype(str)
        .str[:7]
    )

    # Ensure numeric
    df_cohort["period_number"] = pd.to_numeric(
        df_cohort["period_number"],
        errors="coerce"
    )

    df_cohort["retention_rate"] = pd.to_numeric(
        df_cohort["retention_rate"],
        errors="coerce"
    )

    # ============================================================
    # PIVOT
    # ============================================================

    cohort_pivot = df_cohort.pivot(
        index="cohort_month",
        columns="period_number",
        values="retention_rate"
    )

    # ============================================================
    # REAL FIX:
    # Force categorical labels after pivot
    # ============================================================

    cohort_pivot.index = cohort_pivot.index.astype(str).str[:7]

    # Sort descending (latest cohort on top)
    cohort_pivot = cohort_pivot.sort_index(ascending=False)

    # ============================================================
    # RENAME COLUMNS
    # ============================================================

    cohort_pivot.columns = [
        f"Month {int(col)}"
        for col in cohort_pivot.columns
    ]

    # ============================================================
    # HEATMAP
    # ============================================================

    fig = px.imshow(
        cohort_pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(
            x="Period",
            y="Cohort Month",
            color="Retention %"
        )
    )

    # ============================================================
    # IMPORTANT:
    # Prevent Plotly date-axis auto parsing
    # ============================================================

    fig.update_yaxes(type="category")

    fig.update_layout(
        title="Cohort Retention Heatmap",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # KPI CARDS
    # ============================================================

    col1, col2 = st.columns(2)

    try:
        month0 = cohort_pivot.iloc[:, 0].mean()
    except:
        month0 = 100

    try:
        month1 = cohort_pivot.iloc[:, 1].mean()
    except:
        month1 = 0

    with col1:
        st.metric(
            "Month-0 Retention",
            f"{month0:.0f}%"
        )

    with col2:
        st.metric(
            "Month-1 Retention",
            f"{month1:.2f}%"
        )

    # ============================================================
    # BUSINESS INSIGHT
    # ============================================================

    st.info(f"""
    Key Insight: Only {month1:.2f}% of customers returned in Month-1.
    Near-zero retention suggests weak repeat purchase behavior
    and lack of post-purchase engagement strategy.
    """)

    # ============================================================
    # METHODOLOGY NOTE
    # ============================================================

    st.markdown("---")

    st.subheader("📘 Methodology Notes")

    st.warning("""
    Event-level sampling can distort retention analysis because
    future user activity may be excluded from sampled datasets.

    To preserve longitudinal behavioral continuity,
    retention analysis should use user-level sampling
    where all events from sampled users are retained.
    """)

